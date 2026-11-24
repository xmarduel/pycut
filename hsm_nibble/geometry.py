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

from shapely.geometry import MultiPolygon, Point, Polygon  # type: ignore

from hsm_nibble.arc_utils import (  # type: ignore
    ArcData, ArcDir, LineData, StartPointTactic,
    complete_arc, create_arc, create_arc_from_path,
    create_circle, mirror_arc, split_arcs,
)
from hsm_nibble.path_assembler import PathAssembler  # type: ignore
from hsm_nibble.path_planner import PathPlanner  # type: ignore
from hsm_nibble.debug import Display
from hsm_nibble.voronoi_centers import VoronoiCenters  # type: ignore
DEBUG_DISPLAY = Display()


# Filter arcs that are entirely within this distance of a pocket edge.
SKIP_EDGE_ARCS = 1 / 20


class BaseGeometry:
    # Area we have calculated arcs for. Calculated by appending full circles.
    calculated_area_total: Polygon

    starting_cut_area: Polygon

    def __init__(
            self,
            to_cut: Polygon | MultiPolygon,
            step: float,
            winding_dir: ArcDir,
            already_cut: Polygon = None,
            assembler: PathAssembler | None = None,
    ) -> None:
        self.polygon: Polygon | MultiPolygon = to_cut
        self.step: float = step
        self.winding_dir: ArcDir = winding_dir
        if already_cut is None:
            already_cut = Polygon()
        self.starting_cut_area = already_cut

        self.calculated_area_total = self.starting_cut_area.buffer(0)
        cut_area_initial = self.starting_cut_area.buffer(0)
        # Not the same instance.
        assert self.calculated_area_total is not cut_area_initial

        self._filter_input_geometry()
        self.dilated_starting_polygon = self.polygon.buffer(self.step / 10)

        if assembler is None:
            self.assembler = PathAssembler(
                step, winding_dir, cut_area_initial, self.dilated_starting_polygon)
        else:
            self.assembler = assembler

    # Properties that delegate to the assembler so the rest of the code can
    # continue to use self.path, self.last_arc, self.cut_area_total.

    @property
    def path(self) -> list[ArcData | LineData]:
        return self.assembler.path

    @property
    def last_arc(self) -> ArcData | None:
        return self.assembler.last_arc

    @property
    def cut_area_total(self) -> Polygon:
        return self.assembler.cut_area_total

    @cut_area_total.setter
    def cut_area_total(self, value: Polygon) -> None:
        self.assembler.cut_area_total = value

    @property
    def pending_arc_queues(self) -> list[list[ArcData]]:
        return self.assembler.pending_arc_queues

    def _filter_input_geometry(self) -> None:
        """Normalise and validate the input polygon before path generation.

        Accepts either a Polygon or MultiPolygon and ensures self.polygon is
        always a MultiPolygon on exit.  Steps performed:

        1. Coerce a bare Polygon into a single-element MultiPolygon.
        2. Drop any non-Polygon sub-geometries (e.g. LineStrings or Points
           that can appear after a boolean difference).
        3. Repair each sub-polygon with buffer(0) if it is not valid.
        4. Discard sub-polygons that vanish when inset by step/10 — these
           are too small to contribute a meaningful toolpath arc.
        5. Repair the reassembled MultiPolygon if overlapping sub-polygons
           have made it invalid.
        """
        if self.polygon.geom_type == "Polygon":
            geoms = [self.polygon]
        else:
            geoms = [g for g in self.polygon.geoms if g.geom_type == "Polygon"]

        # Repair each sub-polygon individually, then filter out tiny ones.
        repaired = []
        for poly in geoms:
            if not poly.is_valid:
                poly = poly.buffer(0)
            # buffer(0) on a self-intersecting polygon can return a MultiPolygon;
            # flatten it so no geometry is silently dropped.
            if poly.geom_type == "MultiPolygon":
                candidates = list(poly.geoms)
            elif poly.geom_type == "Polygon":
                candidates = [poly]
            else:
                continue
            for candidate in candidates:
                if candidate.buffer(-self.step / 10).area <= 0:
                    continue
                repaired.append(candidate)

        self.polygon = MultiPolygon(repaired)

        # Repair the combined MultiPolygon if overlaps are present.
        if not self.polygon.is_valid:
            self.polygon = self.polygon.buffer(0)


    def _flush_arc_queues(self) -> None:
        self.assembler.flush_arc_queues()

    def _queue_arcs(self, new_arcs: list[ArcData]) -> None:
        self.assembler.queue_arcs(new_arcs)

    def _split_arcs(self, full_arcs: list[ArcData]) -> list[ArcData]:
        return split_arcs(full_arcs, self.calculated_area_total)


class Pocket(BaseGeometry):
    """
    A CAM library to generate a HSM "peeling" pocketing toolpath.
    """

    start_point: Point
    max_starting_radius: float
    starting_angle: float | None = None
    last_arc: ArcData | None
    last_circle: ArcData | None
    debug: bool = False

    def __init__(
            self,
            to_cut: Polygon,
            step: float,
            winding_dir: ArcDir,
            already_cut: Polygon | None = None,
            generate: bool = False,
            voronoi: VoronoiCenters | None = None,
            starting_point_tactic: StartPointTactic = StartPointTactic.WIDEST,
            starting_point: Point | None = None,
            starting_radius: float | None = None,
            debug: bool = False,
    ) -> None:
        """
        Arguments:
            to_cut: The area this pocket should cover.
            step: The distance between cutting path passes.
            winding_dir: Tactic for choosing clockwise or anticlockwise path sections.
            already_cut: An area where no cutting path should be generated but
                also no care needs to be taken when intersecting it. Also rapid moves
                may pass through it.
            generate: Whether to use the get_arcs(...) parameter as a generator
                function (True) or calculate the whole path at the start (False).
            voronoi: Optionally pass in a voronoi diagram detailing points equidistant
                from the part edges. If not provided, one will be created.
            starting_point_tactic: Tactic used to pick the very start of the cutting
                path.
            starting_point: Override the automatically calculated cutting path start point.
                Must be withing either the `to_cut` area or the `already_cut` area if
                one was specified.
            starting_radius: Optionally set the required space at the start_point.
                Used to make sure an entry helix has enough space at the start_point
                when machining.

        Properties:
            start_point: The start of the cutting path. If one is not specified with
                the starting_point parameter, this will be calculated automatically.
            max_starting_radius: The maximum radius a circle at start_point could
                be without overlapping the part's edges.
            starting_angle: `None` if the entry circle is completely within the already_cut
                area. Otherwise it contains the angle to the start of the cutting path
                where the entry circle intersects the cutting path.
        """
        if already_cut is None:
            already_cut = Polygon()
        complete_pocket = already_cut.union(to_cut)
        to_cut = complete_pocket.difference(already_cut)

        self.starting_cut_area = already_cut
        self.starting_radius = starting_radius
        self.generate = generate
        self.debug = debug

        # Calculate voronoi diagram for finding points equidistant between part edges.
        if voronoi is None:
            if starting_point is not None:
                voronoi = VoronoiCenters(complete_pocket, starting_point=starting_point)
            elif starting_point_tactic == StartPointTactic.WIDEST:
                voronoi = VoronoiCenters.for_widest_start(
                        self.starting_radius, step, complete_pocket, already_cut)
            elif starting_point_tactic == StartPointTactic.PERIMETER:
                voronoi = VoronoiCenters.for_perimeter_start(
                        self.starting_radius or step, complete_pocket, already_cut)

            assert voronoi is not None
        self.voronoi = voronoi

        # Calculate entry hole settings.
        self.max_starting_radius = voronoi.max_starting_radius
        if starting_radius and self.max_starting_radius < starting_radius:
            print(f"Warning: Starting radius of {starting_radius} overlaps boundaries "
                  f"at {voronoi.start_point}")
            print(f" Largest possible at this location: {round(self.max_starting_radius, 3)}")
        if self.starting_radius is not None:
            radius = min(self.starting_radius, self.max_starting_radius)
            start_circle = voronoi.start_point.buffer(radius)
            already_cut = already_cut.union(start_circle)

        super().__init__(to_cut, step, winding_dir, already_cut=already_cut)

        self._reset()
        self.calculate_path()

    def _reset(self) -> None:
        """ Cleanup and/or initialise everything. """

        self.start_point: Point = self.voronoi.start_point
        self.start_radius: float = self.voronoi.start_distance or 0

        # Used to detect when an arc is too close to the edge to be worthwhile.
        dilated_polygon_boundaries = []
        multi = self.polygon
        if multi.geom_type != "MultiPolygon":
            multi = MultiPolygon([multi])
        for poly in multi.geoms:
            for ring in [poly.exterior] + list(poly.interiors):
                dilated_polygon_boundaries.append(
                        ring.buffer(self.step * SKIP_EDGE_ARCS))

        # Generate first circle from which other arcs expand.
        # Pass the shared assembler so EntryCircle appends directly to our path.
        entry_circle = EntryCircle(
                self.polygon,
                self.start_point,
                self.start_radius,
                self.step,
                self.winding_dir,
                already_cut=self.calculated_area_total,
                assembler=self.assembler)
        entry_circle.spiral()
        entry_circle.circle()

        if self.starting_radius is not None:
            radius = min(self.starting_radius, self.max_starting_radius)
            if (self.path and
                    self.start_point.buffer(radius).distance(
                        self.path[0].start) < self.step / 20):
                assert self.path[0].start
                dx = self.path[0].start.x - self.start_point.x
                dy = self.path[0].start.y - self.start_point.y
                self.starting_angle = math.atan2(dx, dy)

        # Seed last_circle so the first arc is spaced correctly from centre.
        # Compute the initial planning area before creating PathPlanner so it
        # can be passed in and used consistently for arc fitting.
        last_circle = create_circle(self.start_point, self.start_radius)
        self.calculated_area_total = self.calculated_area_total.union(
                Polygon(last_circle.path))

        # Create the planner that will drive the voronoi traversal.
        self.path_planner = PathPlanner(
            voronoi=self.voronoi,
            step=self.step,
            winding_dir=self.winding_dir,
            assembler=self.assembler,
            polygon=self.polygon,
            dilated_polygon_boundaries=dilated_polygon_boundaries,
            generate=self.generate,
            debug=self.debug,
            calculated_area=self.calculated_area_total,
        )
        self.path_planner.last_circle = last_circle

    def calculate_path(self) -> None:
        """ Reset path and restart from beginning. """
        # Create the generator.
        generator = self.get_arcs()

        if not self.generate:
            # Don't want to use it as a generator so set it running.
            try:
                next(generator)
            except StopIteration:
                pass

    def done_generating(self):
        if DEBUG_DISPLAY:
            DEBUG_DISPLAY.display(
                    polygons={
                        "previously_cut": self.starting_cut_area,
                        "to_cut": self.polygon,
                        "to_cut_dilated": self.dilated_starting_polygon,
                        #"cut_progress": self.calculated_area_total,
                        },
                    voronoi=self.voronoi,
                    path=self.path
                    )

    def get_arcs(self, timeslice: int = 0):
        """
        Generator that creates the toolpath. Delegates to PathPlanner.generate_path.

        Yields an estimated ratio of path completion when generate=True.
        """
        yield from self.path_planner.generate_path(timeslice)
        self.done_generating()

    @property
    def path_fail_count(self) -> int:
        return self.path_planner.stuck_edge_count

    @property
    def visited_edges(self):
        return self.path_planner.visited_edges

    @property
    def loop_count(self) -> int:
        return self.path_planner.convergence_iterations

class EntryCircle(BaseGeometry):
    center: Point
    radius: float
    start_angle: float

    def __init__(
            self,
            to_cut: Polygon,
            center: Point,
            radius: float,
            step: float,
            winding_dir: ArcDir,
            start_angle: float = 0,
            already_cut: Polygon | None = None,
            assembler: PathAssembler | None = None) :
        super().__init__(to_cut, step, winding_dir, already_cut, assembler=assembler)

        self.center = center
        self.radius = radius
        self.start_angle = start_angle

    def spiral(self):
        loop: float = 0.25
        offset: list[float] = [0.0, 0.0]
        new_arcs = []
        mask = self.center.buffer(self.radius)
        not_done = True
        while loop * self.step <= self.radius and not_done:
            orientation = round(loop * 4) % 4
            if orientation == 0:
                start_angle: float = 0
                offset[1] -= self.step / 4
                section_radius = loop * self.step
            elif orientation == 1:
                start_angle = math.pi / 2
                offset[0] -= self.step / 4
                section_radius = loop * self.step
            elif orientation == 2:
                start_angle = math.pi
                offset[1] += self.step / 4
                section_radius = loop * self.step
            elif orientation == 3:
                start_angle = 3 * math.pi / 2
                offset[0] += self.step / 4
                section_radius = loop * self.step
            else:
                raise RuntimeError(f"Unexpected orientation: {orientation}")

            section_center = Point(self.center.x + offset[0], self.center.y + offset[1])
            new_arc = create_arc(
                    section_center, section_radius, start_angle, math.pi / 2, ArcDir.CW)
            assert new_arc is not None

            if new_arc.path.intersects(mask.exterior):
                # Spiral has crossed bounding circle.
                masked_arc = new_arc.path.intersection(mask)
                if masked_arc.geom_type == "MultiLineString":
                    longest = None
                    for arc in list(masked_arc.geoms):
                        if not longest or arc.length > longest.length:
                            longest = arc
                    masked_arc = longest
                if masked_arc.geom_type == "GeometryCollection":
                    longest = None
                    for arc in list(masked_arc.geoms):
                        if not longest or arc.length > longest.length:
                            longest = arc
                    masked_arc = longest

                assert new_arc.radius is not None
                new_arc = create_arc_from_path(
                        new_arc.origin, masked_arc, new_arc.radius, ArcDir.CW)
                new_arc = complete_arc(new_arc, new_arc.winding_dir)
                assert new_arc is not None

                not_done = False

            if self.winding_dir == ArcDir.CCW:
                new_arc = mirror_arc(self.center.x, new_arc)

            new_arcs.append(new_arc)
            loop += 0.25  # 1/4 turn.

        # Add a 1/4-circle arc that starts exactly where the spiral's last arc
        # ends, centred on the starting circle centre.  This bridges the gap
        # between the spiral's outer edge and the starting circle perimeter
        # without introducing a direction discontinuity at the join point.
        if new_arcs:
            last_end = Point(new_arcs[-1].path.coords[-1])
            dx = last_end.x - self.center.x
            dy = last_end.y - self.center.y
            exit_angle = math.atan2(dx, dy)
            exit_radius = self.center.distance(last_end)
            span = math.pi / 2 if self.winding_dir == ArcDir.CW else -math.pi / 2
            closing_arc = create_arc(self.center, exit_radius, exit_angle, span, self.winding_dir)
            if closing_arc is not None:
                new_arcs.append(closing_arc)

        sorted_arcs = self._split_arcs([a for a in new_arcs if a is not None])
        sorted_arcs = [a for a in [complete_arc(s) for s in sorted_arcs] if a is not None]
        self._queue_arcs(sorted_arcs)

        self._flush_arc_queues()

    def circle(self):
        if self.winding_dir == ArcDir.CCW:
            angle = -math.pi * 1.99999
        else:
            angle = math.pi * 1.99999

        new_arc = create_arc(self.center, self.radius, 0, angle, self.winding_dir)
        assert new_arc is not None
        sorted_arcs = self._split_arcs([new_arc])
        sorted_arcs = [a for a in [complete_arc(s) for s in sorted_arcs] if a is not None]
        self._queue_arcs(sorted_arcs)
        self._flush_arc_queues()
