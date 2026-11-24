"""
    A CAM library for generating HSM "peeling" toolpaths from supplied geometry.

    Copyright (C) <2022>  <duncan law>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    mrdunk@gmail.com
"""

import math

from shapely.geometry.base import BaseGeometry  # type: ignore
from shapely.geometry import box, LineString, MultiLineString, Point, Polygon  # type: ignore
from shapely.ops import linemerge, nearest_points  # type: ignore
from shapely.validation import make_valid  # type: ignore

import pyvoronoi  # type: ignore

from hsm_nibble.helpers import log  # type: ignore

Vertex = tuple[float, float]

# Number of decimal places resolution for coordinates.
ROUND_DP = 5

# Resolution of voronoi algorithm.
# Set it to 1 better than the geometry resolution.
VORONOI_RES = 10**(ROUND_DP + 1)

# A small number for comparing things that should touch if not for floating-point error.
#EPS = 5.96e-08
EPS = 1 / (10 ** ROUND_DP)


class PointOutsidePart(Exception):
    pass


def round_coord(value: tuple[float, float], dp: int = ROUND_DP) -> tuple[float, float]:
    return (round(value[0], dp), round(value[1], dp))


class VoronoiGraph:
    """
    Stores the graph of Voronoi edges and vertices, and provides the primitive
    operations for mutating it.  Extracted from VoronoiCenters so the data
    structures and their invariants can be understood and tested in isolation.
    """

    def __init__(self) -> None:
        self.edges: dict[int, LineString] = {}
        self.vertex_to_edges: dict[Vertex, list[int]] = {}
        self.edge_to_vertex: dict[int, tuple[Vertex, Vertex]] = {}
        self.edge_count: int = 0

    def check(self) -> None:
        """Sanity check data structures."""
        for edge_i, edge in self.edges.items():
            assert edge_i in self.edge_to_vertex
            vertices = self.edge_to_vertex[edge_i]
            assert len(vertices) == 2
            assert edge.coords[0] in vertices
            assert edge.coords[-1] in vertices
            assert edge.coords[0] != edge.coords[-1]  # Loop
            assert vertices[0] in self.vertex_to_edges
            assert vertices[1] in self.vertex_to_edges

        for edge_i, vertices in self.edge_to_vertex.items():
            assert edge_i in self.edges
            assert len(vertices) == 2
            assert vertices[0] in self.vertex_to_edges
            assert vertices[1] in self.vertex_to_edges

        for vertex, edges_i in self.vertex_to_edges.items():
            assert len(set(edges_i)) == len(edges_i)  # Loop
            for edge_i in edges_i:
                assert edge_i in self.edges
                vertices = self.edge_to_vertex[edge_i]
                assert vertex in vertices

    def store(self, edge: LineString | MultiLineString, replace_index: int | None = None) -> None:
        """Store a Voronoi edge and associated vertices in the internal data structures."""
        assert edge.geom_type == "LineString", f"linemerge failed: {edge}"

        if edge.length == 0:
            return

        edge_index = replace_index
        if edge_index is None:
            edge_index = self.edge_count
            self.edge_count += 1
        vert_index_a = (edge.coords[0][0], edge.coords[0][1])
        vert_index_b = (edge.coords[-1][0], edge.coords[-1][1])

        self.edges[edge_index] = edge  # pyright: ignore[reportArgumentType]
        self.vertex_to_edges.setdefault(vert_index_a, []).append(edge_index)
        self.vertex_to_edges.setdefault(vert_index_b, []).append(edge_index)
        self.edge_to_vertex[edge_index] = (vert_index_a, vert_index_b)

    def remove(self, edge_index: int) -> None:
        """Remove a Voronoi edge and associated vertices from the internal data structures."""
        if len(self.edges) <= 1:
            # Special case when cleaning up edges and the polygon is a simple circle.
            return
        vert_a, vert_b = self.edge_to_vertex[edge_index]
        neibours_a = self.vertex_to_edges[vert_a]
        neibours_b = self.vertex_to_edges[vert_b]

        neibours_a.remove(edge_index)
        neibours_b.remove(edge_index)
        if not neibours_a:
            del self.vertex_to_edges[vert_a]
        if not neibours_b:
            del self.vertex_to_edges[vert_b]
        del self.edge_to_vertex[edge_index]
        del self.edges[edge_index]

    def vertexes_to_edge(self, vert_a: Vertex, vert_b: Vertex) -> int | None:
        """
        Args:
            vert_a: First vertex.
            vert_b: Second vertex.
        Returns:
            The edge between vert_a and vert_b, or None if no such edge exists.
        """
        for e in self.vertex_to_edges[vert_a]:
            if e in self.vertex_to_edges[vert_b]:
                return e
        return None


class VoronoiCenters:
    """
    A wrapper for pyvoronoi that calculates midpoints equidistant to 2 or more polygon
    edges.
    While pyvoronoi does not natively handle arcs and circles, this wrapper attempts
    to prune voronoi edges that are produced by arcs that have been split into line
    segments.
    """

    def __init__(
            self,
            polygon: Polygon,
            tolerence: float = 1.01,
            preserve_widest: bool = False,
            preserve_edge: bool = False,
            starting_point: Point | None = None
            ) -> None:
        """
        Arguments:
            polygon: The geometer that we wish to generate a voronoi diagram inside.
            tolerence: Parameter used for pruning unwanted voronoi edges. This should
                be approximately the same as the maximum expected jitter in
                geometry coordinates.
        """
        self.graph = VoronoiGraph()

        if not polygon:
            return

        assert preserve_widest or preserve_edge or starting_point is not None, "No valid starting point specified"

        self.polygon = polygon
        self._validate_poly()
        self.tolerence = tolerence

        self.max_dist = max((self.polygon.bounds[2] - self.polygon.bounds[0]),
                            (self.polygon.bounds[3] - self.polygon.bounds[1])) + 1

        # Collect polygon segments to populate voronoi with.
        geom_primatives: list[tuple[Vertex, Vertex]] = []
        outlines = [self.polygon.exterior] + list(self.polygon.interiors)
        for outline in outlines:
            prev_point = None
            first_point = None
            for point in outline.coords:
                if prev_point is None:
                    first_point = point
                    prev_point = point
                elif point == prev_point:
                    continue
                else:
                    geom_primatives.append((prev_point, point))
                    prev_point = point
            assert prev_point == first_point  # This is a loop.

        # Generate voronoi diagram.
        pv = pyvoronoi.Pyvoronoi(VORONOI_RES)
        for segment in geom_primatives:
            #pv.AddSegment(segment)
            pv.AddSegment(list(segment)) # PyVoronoi-1.2.4
        pv.Construct()

        edges = pv.GetEdges()
        vertices = pv.GetVertices()
        cells = pv.GetCells()

        # Parse voronoi diagram. Store data as shapely LineSegment.
        visited_edges: set[int] = set()
        for edge_index, edge in enumerate(edges):
            if edge_index in visited_edges:
                continue
            visited_edges.add(edge_index)
            visited_edges.add(edge.twin)

            start_vert = vertices[edge.start]
            end_vert = vertices[edge.end]
            if edge.twin and edge.is_primary:
                p_start = Point(round_coord((start_vert.X, start_vert.Y)))
                p_end = Point(round_coord((end_vert.X, end_vert.Y)))
                if (p_start.distance(self.polygon) <= EPS and
                        p_end.distance(self.polygon) <= EPS):
                    if edge.is_linear:
                        line = LineString((
                            round_coord((start_vert.X, start_vert.Y)),
                            round_coord((end_vert.X, end_vert.Y))
                        ))
                        self.graph.store(line)
                    else:
                        cell = cells[edge.cell]
                        cell_twin = cells[edges[edge.twin].cell]

                        geom_points = []
                        geom_edges = []
                        if cell.contains_point:
                            geom_points.append(pv.RetrieveScaledPoint(cell))
                        if cell_twin.contains_point:
                            geom_points.append(
                                pv.RetrieveScaledPoint(cell_twin))
                        if cell.contains_segment:
                            geom_edges.append(pv.RetrieveScaledSegment(cell))
                        if cell_twin.contains_segment:
                            geom_edges.append(
                                pv.RetrieveScaledSegment(cell_twin))
                        assert len(geom_edges) > 0
                        assert len(geom_points) + len(geom_edges) == 2

                        if len(geom_points) == 1 and len(geom_edges) == 1:
                            start_point = Point(round_coord(
                                (start_vert.X, start_vert.Y)))
                            end_point = Point(round_coord(
                                (end_vert.X, end_vert.Y)))
                            max_distance = start_point.distance(end_point) / 10 + 0.01
                            points = (round_coord(point)
                                      for point in
                                      pv.DiscretizeCurvedEdge(edge_index, max_distance))
                            self.graph.store(LineString(points))
                        else:
                            # A parabola between 2 lines (as opposed to 1 line and one point)
                            # leaves the DiscretizeCurvedEdge() function broken sometimes.
                            # Let's just assume a straight line edge in these cases.
                            # This is a particular problem when duplicate points in
                            # input data create a line of zero length.
                            log(f"BORKED VORONOI: \tgeom_points: {geom_points}\tgeom_edges: {geom_edges}")
                            line = LineString((
                                round_coord((start_vert.X, start_vert.Y)),
                                round_coord((end_vert.X, end_vert.Y))
                            ))
                            self.graph.store(line)
                        continue

        preserve = set()
        if preserve_widest:
            # Picks a start_point at the widest point of the input shape.
            # We want to ensure the start_point is not cleaned up when simplifying edges.
            self.start_point, self.start_distance = self.widest_gap()
            preserve.add(self.start_point.coords[0])
        if preserve_edge:
            # Picks a start_point that touches the perimeter.
            # We want to ensure the start_point is not cleaned up when simplifying edges.
            self.start_point = self.vertex_on_perimiter()
            preserve.add(self.start_point.coords[0])
            self.start_distance = 0

        self._drop_irrelevant_edges(preserve)

        if starting_point is not None:
            # Set the starting point.
            self.set_starting_point(starting_point)
            preserve.add(self.start_point.coords[0])

        self._split_on_pocket_edge()
        self._combine_edges(preserve)
        self._remove_trivial(preserve)

        self.max_starting_radius = self.distance_from_geom(self.start_point)

        self.graph.check()

    def _validate_poly(self) -> None:
        """
        Make sure input geometry is sane.
        Do some quick fixes on common issues.
        """
        fixed = self.polygon
        while fixed.geom_type != "Polygon":
            # We iterate the geoms in any collection, and blindly use the largest Polygon found.
            # This isn't a great aproach. Whatever code calls this should only have sent a single
            # Polygon.
            candidates = [make_valid(g) for g in fixed.geoms if g.geom_type == "Polygon"]
            if not candidates:
                raise ValueError(f"make_valid returned {fixed.geom_type} with no Polygon components")
            fixed = max(candidates, key=lambda g: g.area)
            fixed = make_valid(fixed)
        assert isinstance(fixed, Polygon)
        self.polygon = fixed

        # Any jitter in input geometry may make points appear out of sequence
        # leading to invalid geometry.
        # See here for what valid geometry looks like:
        # https://shapely.readthedocs.io/en/latest/manual.html#polygons
        # .simplify(...) will fix issues caused by input coordinate jitter.
        self.polygon = self.polygon.simplify(0.05)

    def distance_from_geom(self, point: BaseGeometry) -> float:
        """
        Distance form nearest geometry edge. Note this edge may be the outer
        boundary or the edge of an island.
        """
        distance = min(self.max_dist, self.polygon.boundary.distance(point))
        return distance

    def _combine_edges(self, dont_merge: set[tuple[float, float]]) -> None:
        """
        For any voronoi vertex with only 2 edges meeting there, combine the
        voronoi edges, removing the vertex.
        """
        to_merge = []
        for vertex, edges_i in self.graph.vertex_to_edges.items():
            if len(edges_i) == 2 and vertex not in dont_merge:
                to_merge.append(vertex)

        while to_merge:
            candidate = to_merge.pop()
            edges_i = self.graph.vertex_to_edges[candidate]
            assert len(edges_i) == 2

            if edges_i[0] not in self.graph.edges or edges_i[1] not in self.graph.edges:
                # Already done.
                continue

            edge_i_a = edges_i[0]
            edge_i_b = edges_i[1]

            edge_a = self.graph.edges[edge_i_a].coords
            edge_b = self.graph.edges[edge_i_b].coords

            if edge_a[0] in [edge_b[0], edge_b[-1]] and edge_a[-1] in [edge_b[0], edge_b[-1]]:
                # Loop with no branches. "Circle on a stick."
                # It wold be possible to combine the last 2 segments but that
                # would confuse linemerge(...) as it would not know which pair
                # of ends to make the beginning and end of the LineString.
                continue

            self.graph.remove(edge_i_a)
            self.graph.remove(edge_i_b)

            edge_combined = linemerge([edge_a, edge_b])
            self.graph.store(edge_combined, edge_i_a)

    def _remove_trivial(self, preserve: set[tuple[float, float]]) -> None:
        """Collapse any edge that is too short to care about."""
        # First the easy cases: The short edges with no connections at one end.
        further_consideration = set()
        run = True
        while run:
            run = False
            for edge_i, edge in self.graph.edges.items():
                if edge.length < EPS * 10 and len(self.graph.edges) > 1:
                    vert_a, vert_b = self.graph.edge_to_vertex[edge_i]
                    if len(self.graph.vertex_to_edges[vert_a]) == 1 and vert_a not in preserve:
                        self.graph.remove(edge_i)
                        run = True
                        break
                    if len(self.graph.vertex_to_edges[vert_b]) == 1 and vert_b not in preserve:
                        self.graph.remove(edge_i)
                        run = True
                        break
                    further_consideration.add(edge_i)

        # Some edges are duplicates of each other, joined at both ends.
        # Like tiny loops.
        still_to_remove: dict[tuple[Vertex, Vertex], set[int]] = {}
        for edge_i in further_consideration:
            vert_a, vert_b = self.graph.edge_to_vertex[edge_i]

            # Make a key that is the same for any edge starting and finishing in the same place.
            key = (vert_a, vert_b)
            if vert_a < vert_b:
                key = (vert_b, vert_a)

            still_to_remove.setdefault(key, set()).add(edge_i)
        for edges_i in still_to_remove.values():
            while len(edges_i) > 1 and len(self.graph.edges) > 1:
                edge_i = edges_i.pop()
                self.graph.remove(edge_i)

        # Duplicates are now gone.
        # Clean up simple lines where appropriate.
        for edges_i in still_to_remove.values():
            edge_i = edges_i.pop()
            vert_a, vert_b = self.graph.edge_to_vertex[edge_i]
            if len(self.graph.vertex_to_edges[vert_a]) == 1 and vert_a not in preserve:
                if len(self.graph.edges) > 1:
                    self.graph.remove(edge_i)
            if len(self.graph.vertex_to_edges[vert_b]) == 1 and vert_b not in preserve:
                if len(self.graph.edges) > 1 and edge_i in self.graph.edges:
                    self.graph.remove(edge_i)

    def _split_on_pocket_edge(self) -> None:
        """
        When an polygon island touches the exterior at a single point the vorinoi
        diagram will have a vertex at that point. This leads code like _combine_edges
        to presume the edge passes through this vertex.
        It is unlikely this is the desired behavior so this method "shrinks" the
        voronoi edges slightly, creating 2 very close vertexes which stop the
        voronoi edges from touching.
        """
        split_at = []
        for vertex, edges_i in self.graph.vertex_to_edges.items():
            point = Point(vertex)
            if len(edges_i) == 2 and self.distance_from_geom(point) <= EPS:
                split_at.append(vertex)

        while split_at:
            vertex = split_at.pop()
            edges_i = self.graph.vertex_to_edges[vertex]

            assert len(edges_i) == 2

            edge_i_0 = edges_i[0]
            edge_0 = self.graph.edges[edge_i_0]
            if edge_0.coords[0] == vertex:
                edge_0 = LineString(edge_0.coords[::-1])
            vertex_updated_0 = edge_0.interpolate(edge_0.length - EPS)

            edge_i_1 = edges_i[1]
            edge_1 = self.graph.edges[edge_i_1]
            if edge_1.coords[0] == vertex:
                edge_1 = LineString(edge_1.coords[::-1])
            vertex_updated_1 = edge_1.interpolate(edge_1.length - EPS)

            self.graph.remove(edge_i_0)
            self.graph.remove(edge_i_1)

            self.graph.store(LineString([edge_0.coords[0], vertex_updated_0]), edge_i_0)
            self.graph.store(LineString([edge_1.coords[0], vertex_updated_1]), edge_i_1)

    def _get_cleanup_candidates(self, edge_i: int, tolerence: float) -> set[int]:
        """ Given an edge as a starting point, follow connected voronoi edges if they are likely candidates to delete.
        Args:
            edge_i: An edge index to start at. One end of the starting edge should have no other edge attached.
            tolerence: Pruning threshold — edges shorter than (distance_to_boundary * tolerence) are candidates.
        Returns:
            A set of edge indexes that are candidates for pruning.
            In the event that an invalid starting position was supplied for edge_i, an empty set will be returned.
        """
        vertices_to_cleanup = []
        vertex_origin = None
        visited_edges = set()
        last_edge_angle = None
        next_edges = set([edge_i])
        previous_vertex_end = None

        while True:
            best_fit_edge_i = None
            best_fit_edge_angle = None
            best_fit_vertex_end = None
            best_fit_angle_diff = 0.3

            # Iterate through all edges adjoining the current candidate's candidate_vertex_end.
            for candidate_edge_i in next_edges:
                candidate_vertex_start, candidate_vertex_end = self.graph.edge_to_vertex[candidate_edge_i]

                if last_edge_angle is None:
                    # First time around the loop.
                    if len(self.graph.vertex_to_edges[candidate_vertex_start]) > 1:
                        # Try to start at the end of the edge with no junctions.
                        candidate_vertex_start, candidate_vertex_end = (
                                candidate_vertex_end, candidate_vertex_start)
                    if len(self.graph.vertex_to_edges[candidate_vertex_start]) > 1:
                        # Trying to start from an edge with junctions at both ends.
                        # This is not a valid starting point.
                        return set()

                    vertex_origin = candidate_vertex_start
                    previous_vertex_end = candidate_vertex_start
                    vertices_to_cleanup.append(candidate_vertex_start)
                else:
                    # Make sure ends are correctly orientated.
                    if candidate_vertex_end == previous_vertex_end:
                        candidate_vertex_start, candidate_vertex_end = candidate_vertex_end, candidate_vertex_start
                assert candidate_vertex_start == previous_vertex_end
                assert vertices_to_cleanup[-1] == candidate_vertex_start

                if (vertex_origin is not None and abs(LineString([vertex_origin, candidate_vertex_end]).length) >=
                        abs(self.distance_from_geom(Point(candidate_vertex_end)) * tolerence)):
                    # If the distance from the start of the original edge to the end of the current candidate
                    # is longer than the distance to the closest polygon perimeter edge,
                    # then the considered edge is a valid voronoi edge and should not be pruned.
                    continue

                candidate_edge_angle = math.atan2(
                    (candidate_vertex_start[0] - candidate_vertex_end[0]),
                    (candidate_vertex_start[1] - candidate_vertex_end[1]))

                if last_edge_angle is None:
                    # First time around the loop.
                    best_fit_edge_angle = candidate_edge_angle
                    best_fit_vertex_end = candidate_vertex_end
                    best_fit_edge_i = candidate_edge_i
                    continue

                # When considering the next candidate to prune, it should be roughly co-linear
                # to the current candidate.
                angle_diff = abs(candidate_edge_angle - last_edge_angle)
                if angle_diff < best_fit_angle_diff:
                    best_fit_angle_diff = angle_diff
                    best_fit_vertex_end = candidate_vertex_end
                    best_fit_edge_i = candidate_edge_i
                    best_fit_edge_angle = candidate_edge_angle

            if best_fit_edge_i is None:
                break

            last_edge_angle = best_fit_edge_angle
            previous_vertex_end = best_fit_vertex_end
            assert previous_vertex_end is not None
            vertices_to_cleanup.append(previous_vertex_end)
            visited_edges.add(best_fit_edge_i)
            next_edges = set(self.graph.vertex_to_edges[previous_vertex_end]).difference(visited_edges)


        # Convert vertexes to edges.
        last_vertex = None
        to_cleanup: set[int] = set()
        for vertex in vertices_to_cleanup:
            if last_vertex:
                connecting_edge = self.graph.vertexes_to_edge(last_vertex, vertex)
                assert connecting_edge is not None
                to_cleanup.add(connecting_edge)
            last_vertex = vertex

        return to_cleanup

    def _drop_irrelevant_edges(self, preserve: set[tuple[float, float]]) -> None:
        """
        If any geometry resulting from a voronoi edge will be covered by the
        geometry of some other voronoi edge it is deemed irrelevant and pruned
        by this function.
        Args:
            preserve: A set of vertexes to be left somewhere in the diagram despite pruning.
        """
        to_prune: set[int] = set()
        for edge_i in self.graph.edges:
            to_prune |= self._get_cleanup_candidates(edge_i, self.tolerence)

        # Any edges with a vertex in the preserve set should be considered more carefully.
        for preserve_vertex in preserve:
            to_preserve = set()
            still_prune = set()
            for edge_i in to_prune:
                vert_a, vert_b = self.graph.edge_to_vertex[edge_i]
                if preserve_vertex in (vert_a, vert_b):
                    if len(self.graph.vertex_to_edges[vert_a]) > 1 and len(self.graph.vertex_to_edges[vert_b]) > 1:
                        # The edge being considered is connected to the main voronoi diagram at both ends.
                        # It should not be pruned.
                        to_preserve.add(edge_i)
                    else:
                        still_prune.add(edge_i)
            for edge_i in to_preserve:
                to_prune.remove(edge_i)
            if not to_preserve and still_prune:
                # Looks like we don't intend to preserve any of the requested vertices.
                # Pick one at random to preserve.
                to_prune.remove(still_prune.pop())

        # The self._get_cleanup_candidates algorithm does not check it isn't suggesting
        # the deletion of an edge that connects some other edge to the main diagram.
        # This could lead to orphaned islands of edges.
        # Here we make sure we only actually remove edges that do not link other
        # edges to the main diagram.
        while True:
            prune_edge = None
            for edge_i in to_prune:
                vert_a, vert_b = self.graph.edge_to_vertex[edge_i]
                if len(self.graph.vertex_to_edges[vert_a]) == 1:
                    prune_edge = edge_i
                    break
                if len(self.graph.vertex_to_edges[vert_b]) == 1:
                    prune_edge = edge_i
                    break
            if prune_edge is None:
                break
            to_prune.remove(prune_edge)
            self.graph.remove(prune_edge)

    def widest_gap(self) -> tuple[Point, float]:
        """
        Return the vertex in vertex_to_edges furthest from any polygon boundary
        (exterior or interior rings), and that distance.
        """
        widest_dist = 0
        widest_point = None
        for vertex in self.graph.vertex_to_edges:
            p = Point(vertex)
            nearest_dist = p.distance(self.polygon.boundary)
            if nearest_dist > widest_dist:
                widest_dist = nearest_dist
                widest_point = p
        assert widest_point is not None
        return (widest_point, widest_dist)

    def vertex_on_perimiter(self) -> Point:
        """
        Find a point as close to the perimeter as possible.
        """
        bounding_box = box(*self.polygon.bounds).exterior
        closest = None
        distance = self.max_dist
        for vertex in self.graph.vertex_to_edges:
            p = Point(vertex)
            if bounding_box.intersects(p):
                return p
            dist = bounding_box.distance(p)
            if dist < distance:
                distance = dist
                closest = p
        assert closest is not None
        return closest

    def set_starting_point(self, point: Point) -> None:
        """
        Set a starting point within the polygon from which to start iterating over
        the voronoi diagram.
        If this point is not on the existing voronoi diagram it will need a new edge
        to be added to the diagram to connect this starting point.
        """
        if not point.within(self.polygon):
            raise PointOutsidePart(f"{point} not inside geometry")

        if point.coords[0] in self.graph.vertex_to_edges:
            # point already exists on voronoi diagram. Nothing to do.
            self.start_point = point
            self.start_distance = self.distance_from_geom(point)
            return

        # Find closest voronoi edge to point but only across self.polygon.
        # Closest distances that go outside self.polygon are not valid.
        closest_edge_index = None
        closest_dist = None
        new_vertex = None
        new_edge = None
        for edge_index, edge in self.graph.edges.items():
            dist = edge.distance(point)
            proposed_new_vertex = round_coord(nearest_points(edge, point)[0].coords[0])
            proposed_new_edge = LineString([point, proposed_new_vertex])
            if closest_dist is None or dist < closest_dist:
                if proposed_new_edge.within(self.polygon) or proposed_new_edge.length == 0:
                    closest_dist = dist
                    closest_edge_index = edge_index
                    new_vertex = proposed_new_vertex
                    new_edge = proposed_new_edge

        assert closest_edge_index is not None

        # Add the new vertex on the voronoi graph.
        v1, v2 = self.graph.edge_to_vertex[closest_edge_index]
        new_edge_1 = LineString([v1, new_vertex])
        new_edge_2 = LineString([v2, new_vertex])
        self.graph.remove(closest_edge_index)
        if new_edge_1.length > 0:
            self.graph.store(new_edge_1)
        if new_edge_2.length > 0:
            self.graph.store(new_edge_2)

        # New vertex
        if new_edge is None or new_edge.length == 0:
            new_vertex_point = Point(new_vertex)
            assert point.equals(new_vertex_point)
            self.start_point = new_vertex_point
            self.start_distance = self.distance_from_geom(new_vertex_point)
            return

        # Add a new edge to the voronoi graph.
        # This will home the new starting point.
        assert not point.equals(Point(new_vertex))
        self.graph.store(new_edge)
        self.start_point = point
        self.start_distance = self.distance_from_geom(point)
        return


    @classmethod
    def for_widest_start(
            cls,
            desired_radius: float | None,
            step: float,
            pocket: BaseGeometry,
            already_cut: Polygon | None = None
            ) -> "VoronoiCenters":
        """
        Calculate voronoi diagram with the start point to be in the widest space,
        furthest from any part edge.
        Used when performing pocketing machining operations when cuts should start
        in the area with the most material to be removed. IE: furthest from the part
        perimeter.

        Args:
            desired_radius: Size of desired starting hole.
            step: Pocket algorithm's step size. already_cut will be oversized by this amount.
            pocket: The area the returned voronoi diagram will be calculated for.
            already_cut: The area which must contain the starting hole.

        Returns:
            An instance of VoronoiCenters.
            Of particular interest are the .start_point and .max_desired_radius parameters.
        """
        if already_cut is None:
            complete_pocket = pocket
        else:
            complete_pocket = already_cut.union(pocket)

        voronoi = cls(complete_pocket, preserve_widest=True)
        start = voronoi.start_point
        if desired_radius:
            start = start.buffer(desired_radius)
        if already_cut and not start.within(already_cut.buffer(-step / 2)):
            # Start point outside cut area.
            # Generate a voronoi diagram of just the cut area and take the
            # start point from that.
            cut_voronoi = cls(already_cut, preserve_widest=True)
            voronoi = cls(complete_pocket, starting_point=cut_voronoi.start_point)

        return voronoi

    @classmethod
    def for_perimeter_start(
            cls,
            desired_radius: float,
            pocket: BaseGeometry,
            already_cut: Polygon
            ) -> "VoronoiCenters":
        """
        Calculate voronoi diagram with the start point to be inside the cut area,
        adjacent to the perimeter.
        Used when performing outer-peel machining operations when cuts start at the
        outside and work in towards the perimeter of the part.

        Args:
            desired_radius: Size of desired starting hole.
            pocket: The area the returned voronoi diagram will be calculated for.
            already_cut: The area which must contain the starting hole.

        Returns:
            An instance of VoronoiCenters.
            Of particular interest are the .start_point and .max_desired_radius parameters.
        """
        complete_pocket = already_cut.union(pocket)

        voronoi = cls(complete_pocket, preserve_edge=True)

        perimiter_point = voronoi.start_point
        assert perimiter_point is not None
        voronoi_edge_index = voronoi.graph.vertex_to_edges[perimiter_point.coords[0]]
        assert len(voronoi_edge_index) == 1
        voronoi_edge = voronoi.graph.edges[voronoi_edge_index[0]]
        cut_edge_section = already_cut.intersection(voronoi_edge)
        if cut_edge_section.length > desired_radius * 2:
            new_start_point = cut_edge_section.interpolate(0.5, normalized=True)
            voronoi = cls(complete_pocket, starting_point=new_start_point)
        else:
            # Can't fit desired_radius here.
            # Look for widest point in already_cut area.
            cut_voronoi = cls(already_cut, preserve_widest=True)
            voronoi = cls(complete_pocket, starting_point=cut_voronoi.start_point)

        return voronoi


# Module-level aliases for backward compatibility.
def start_point_widest(
        desired_radius: float | None,
        step: float,
        pocket: BaseGeometry,
        already_cut: Polygon | None = None
        ) -> VoronoiCenters:
    return VoronoiCenters.for_widest_start(desired_radius, step, pocket, already_cut)


def start_point_perimeter(
        desired_radius: float,
        pocket: BaseGeometry,
        already_cut: Polygon
        ) -> VoronoiCenters:
    return VoronoiCenters.for_perimeter_start(desired_radius, pocket, already_cut)
