"""
PathPlanner: traverses a Voronoi graph and generates toolpath arcs along each
edge, delegating path output to a PathAssembler.
"""

import time

from shapely.geometry import LineString, MultiPolygon, Point, Polygon  # type: ignore

from hsm_nibble.arc_utils import (  # type: ignore
    ArcData, ArcDir,
    filter_arc, split_arcs,
)
from hsm_nibble.arc_fitter import (  # type: ignore
    arc_at_distance, find_best_arc_distance,
)
from hsm_nibble.path_assembler import PathAssembler  # type: ignore
from hsm_nibble.voronoi_centers import VoronoiCenters  # type: ignore
from hsm_nibble.helpers import log  # type: ignore

# Whether to visit short voronoi edges first (True) or try to execute longer
# branches first.
BREADTH_FIRST = False


def _collapse_dupe_points(line: LineString) -> LineString | None:
    """Filter out consecutive duplicate points from a LineString."""
    points = []
    last_point = None
    for point in line.coords:
        if last_point == point:
            continue
        points.append(point)
        last_point = point
    if len(points) < 2:
        return None
    return LineString(points)


class PathPlanner:
    """
    Traverses a Voronoi diagram and generates arcs along each edge.

    Owns:
      - Voronoi traversal state (visited_edges, branch_starts)
      - Arc convergence state (last_circle)
      - Progress / diagnostics counters
    Delegates path output to a PathAssembler.
    """

    def __init__(
            self,
            voronoi: VoronoiCenters,
            step: float,
            winding_dir: ArcDir,
            assembler: PathAssembler,
            polygon: Polygon | MultiPolygon,
            dilated_polygon_boundaries: list,
            generate: bool = False,
            debug: bool = False,
            calculated_area: Polygon | None = None,
    ) -> None:
        self.voronoi = voronoi
        self.step = step
        self.winding_dir = winding_dir
        self.assembler = assembler
        self.polygon = polygon
        self.dilated_polygon_boundaries = dilated_polygon_boundaries
        self.generate = generate
        self.debug = debug

        # Planning area: tracks full circles placed so far (distinct from
        # assembler.cut_area_total, which tracks the actual output arcs and is
        # also updated by join_arcs with buffered fan polygons).
        self.calculated_area_total: Polygon = calculated_area if calculated_area is not None else Polygon()

        self.last_circle: ArcData | None = None
        self.stuck_edge_count: int = 0
        self.convergence_iterations: int = 0
        self.visited_edges: set[int] = set()
        self.branch_starts: dict[int, tuple[float, float]] = {}
        self.path_len_progress: float = 0.0
        self.path_len_total: float = sum(
            e.length for e in voronoi.graph.edges.values())

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate_path(self, timeslice: int = 0):
        """
        Generator that traverses the voronoi graph, placing arcs along each
        edge. Yields a progress ratio (0.0–1.0) when generate=True.
        """
        start_time = round(time.time() * 1000)  # ms

        start_vertex: tuple[float, float] | None = self.voronoi.start_point.coords[0]
        while start_vertex is not None:
            combined_edge = self._merge_voronoi_edges(start_vertex)
            if not combined_edge:
                start_vertex = self._select_next_vertex()
                continue

            dist = 0.0
            best_dist = dist
            max_attempts = int(combined_edge.length * 10 / self.step + 10)
            while abs(dist - combined_edge.length) > self.step / 20 and max_attempts > 0:
                max_attempts -= 1
                dist, new_arcs = self._calculate_arc(combined_edge, dist, best_dist)

                self.path_len_progress -= best_dist
                self.path_len_progress += dist

                best_dist = dist
                self.assembler.queue_arcs(new_arcs)

                if timeslice >= 0 and self.generate:
                    now = round(time.time() * 1000)  # ms
                    if start_time + timeslice < now:
                        yield min(0.999, self.path_len_progress / self.path_len_total)
                        start_time = round(time.time() * 1000)  # ms

            if max_attempts <= 0:
                print(f"stuck: {round(dist, 2)} / {round(combined_edge.length, 2)}")
                self.stuck_edge_count += 1

            start_vertex = self._select_next_vertex(combined_edge.coords[-1])
            self.assembler.flush_arc_queues()

        if timeslice and self.generate:
            yield 1.0

        assert not self.branch_starts
        log(f"convergence_iterations: {self.convergence_iterations}")
        log(f"len(path): {len(self.assembler.path)}")
        log(f"stuck_edge_count: {self.stuck_edge_count}")

    # ------------------------------------------------------------------
    # Voronoi traversal
    # ------------------------------------------------------------------

    def _select_next_vertex(
            self,
            current_pos: tuple[float, float] | None = None,
    ) -> tuple[float, float] | None:
        """
        Choose a vertex with an un-travelled voronoi edge leading from it.

        Prunes branch_starts entries that have already been visited, then
        returns the vertex whose unvisited edge is closest to current_pos
        (or the first available vertex when current_pos is None).
        """
        for edge_i in self.visited_edges:
            if edge_i in self.branch_starts:
                self.branch_starts.pop(edge_i)

        shortest = self.voronoi.max_dist + 1
        closest_vertex: tuple[float, float] | None = None
        closest_edge: int | None = None
        for edge_i, vertex in self.branch_starts.items():
            dist = Point(vertex).distance(Point(current_pos)) if current_pos else 0

            if closest_vertex is None:
                shortest = dist
                closest_vertex = vertex
                closest_edge = edge_i
                if not current_pos:
                    break
            elif dist < shortest:
                closest_vertex = vertex
                closest_edge = edge_i
                shortest = dist

        if closest_edge is not None:
            self.branch_starts.pop(closest_edge)

        self.last_circle = None
        return closest_vertex

    def _merge_voronoi_edges(
            self,
            start_vertex: tuple[float, float],
    ) -> LineString | None:
        """
        Walk a chain of voronoi edges from start_vertex, picking one branch
        at each junction, and return the result as a single LineString.

        Unvisited sibling branches at each junction are recorded in
        branch_starts for later traversal.
        """
        vertex = start_vertex
        line_coords: list[tuple[float, float]] = []

        while True:
            branches = self.voronoi.graph.vertex_to_edges[vertex]
            candidate = None
            longest = 0
            for branch in branches:
                if branch not in self.visited_edges:
                    self.branch_starts[branch] = vertex
                    length = self.voronoi.graph.edges[branch].length
                    if candidate is None:
                        candidate = branch
                    elif BREADTH_FIRST and length < longest:
                        candidate = branch
                    elif not BREADTH_FIRST and length > longest:
                        candidate = branch
                    longest = max(longest, length)

            if candidate is None:
                break

            self.visited_edges.add(candidate)
            edge_coords = self.voronoi.graph.edges[candidate].coords

            if not line_coords:
                line_coords = list(edge_coords)
                if start_vertex != line_coords[0]:
                    line_coords = line_coords[::-1]
            else:
                edge_coords = list(edge_coords)
                if line_coords[-1] == edge_coords[-1]:
                    edge_coords = edge_coords[::-1]
                assert line_coords[0] == start_vertex
                assert line_coords[-1] == edge_coords[0]
                line_coords = line_coords + edge_coords

            vertex = line_coords[-1]

        if not line_coords:
            return None

        return _collapse_dupe_points(LineString(line_coords))

    # ------------------------------------------------------------------
    # Arc calculation
    # ------------------------------------------------------------------

    def _arc_at_distance(
            self, distance: float, voronoi_edge: LineString
    ) -> tuple[Point, float]:
        return arc_at_distance(distance, voronoi_edge, self.voronoi.distance_from_geom)

    def _calculate_arc(
            self,
            voronoi_edge: LineString,
            start_distance: float,
            min_distance: float,
    ) -> tuple[float, list[ArcData]]:
        """
        Find the arc that best fits at the current position along voronoi_edge.

        Returns (best_distance, filtered_arcs).
        """
        assert self.calculated_area_total
        assert self.calculated_area_total.is_valid

        best_distance, best_circle, hidden_at_start, iteration_count, _backwards = \
            find_best_arc_distance(
                voronoi_edge=voronoi_edge,
                start_distance=start_distance,
                min_distance=min_distance,
                step=self.step,
                winding_dir=self.winding_dir,
                calculated_area=self.calculated_area_total,
                last_circle=self.last_circle,
                distance_from_geom=self.voronoi.distance_from_geom,
                max_dist=self.voronoi.max_dist,
            )

        if hidden_at_start:
            self.last_circle = best_circle
            return (best_distance, [])

        self.convergence_iterations += iteration_count

        assert best_circle is not None
        self.last_circle = best_circle

        arcs = split_arcs([best_circle], self.calculated_area_total)
        self.calculated_area_total = self.calculated_area_total.union(
            Polygon(best_circle.path))

        filtered_arcs = [arc for arc in arcs if self._filter_arc(arc)]

        return (best_distance, filtered_arcs)

    def _filter_arc(self, arc: ArcData) -> ArcData | None:
        return filter_arc(arc, self.polygon, self.dilated_polygon_boundaries, self.step)
