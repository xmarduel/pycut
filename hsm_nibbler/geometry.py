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

# pylint: disable=attribute-defined-outside-init

from typing import Dict, Generator, List, NamedTuple, Optional, Set, Tuple, Union

from enum import Enum
import math
import time

from shapely.affinity import rotate  # type: ignore
from shapely.geometry import box, GeometryCollection, LinearRing, LineString, MultiLineString, MultiPoint, MultiPolygon, Point, Polygon  # type: ignore
from shapely.ops import linemerge, split, unary_union  # type: ignore
from shapely.errors import GeometryTypeError

from hsm_nibbler.debug import Display
from hsm_nibbler.voronoi_centers import (
    round_coord,
    start_point_perimeter,
    start_point_widest,
    VoronoiCenters,
)  # type: ignore
from hsm_nibbler.helpers import log  # type: ignore

DEBUG_DISPLAY = Display()


# Filter arcs that are entirely within this distance of a pocket edge.
SKIP_EDGE_ARCS = 1 / 20

# Trivially short lines joining arcs should be filtered.
SHORTEST_RAPID = 1e-6

# Number of tries before we give up trying to find a best-fit arc and just go
# with the best we have found so far.
ITERATION_COUNT = 50

# Whether to visit short voronoi edges first (True) or try to execute longer
# branches first.
# TODO: We could use more long range path planning that take the shortest total
# path into account.
# BREADTH_FIRST = True
BREADTH_FIRST = False

# When arc sizes drop below a certain point, we need to reduce the step size or
# forward motion due to the distance between arcs (step) becomes more than the
# arc diameter.
# This constant is the minimum arc radius, expressed as a multiple of the overlap
# size, size at which we start reducing step size.
CORNER_ZOOM = 2.0
# This constant is how much effect the feature will have. A value of "1" will
# keep the distance between each arc center proportional to the arc size.
CORNER_ZOOM_EFFECT = 1.0


class ArcDir(Enum):
    CW = 0
    CCW = 1
    Closest = 2


class MoveStyle(Enum):
    RAPID_OUTSIDE = 0
    RAPID_INSIDE = 1
    CUT = 2


class StartPointTactic(Enum):
    PERIMETER = 0  # Starting point hint for outer peel. On the outer perimeter.
    WIDEST = 1  # Starting point hint for inner pockets.


ArcData = NamedTuple(
    "Arc",
    [
        ("origin", Point),
        ("radius", Optional[float]),
        ("start", Optional[Point]),
        ("end", Optional[Point]),
        ("start_angle", Optional[float]),
        ("span_angle", Optional[float]),
        ("winding_dir", Optional[ArcDir]),
        # TODO: ("widest_at", Optional[Point]),
        # TODO: ("start_DOC", float),
        # TODO: ("end_DOC", float),
        # TODO: ("widest_DOC", float),
        ("path", LineString),
        ("debug", Optional[str]),
    ],
)

LineData = NamedTuple(
    "Line",
    [
        ("start", Point),
        ("end", Point),
        ("path", LineString),
        ("move_style", MoveStyle),
    ],
)


def clean_linear_ring(ring: LinearRing) -> LinearRing:
    """Remove duplicate points in a LinearRing."""
    new_ring = []
    prev_point = None
    first_point = None
    for point in ring.coords:
        if first_point is None:
            first_point = point
        if point == prev_point:
            continue
        else:
            new_ring.append(point)
            prev_point = point
    assert prev_point == first_point  # This is a loop.

    return LinearRing(new_ring)


def clean_polygon(polygon: Polygon) -> Polygon:
    exterior = clean_linear_ring(polygon.exterior)
    holes = []
    for hole in polygon.interiors:
        holes.append(clean_linear_ring(hole))

    return Polygon(exterior, holes=holes)


def clean_multipolygon(multi: MultiPolygon|Polygon) -> MultiPolygon:
    if multi.geom_type != "MultiPolygon":
        multi = MultiPolygon([multi])
    polygons = []
    for polygon in multi.geoms:
        polygons.append(clean_polygon(polygon))

    return MultiPolygon(polygons)


def create_circle(
    origin: Point, radius: float, winding_dir: Optional[ArcDir] = None
) -> ArcData:
    """
    Generate a circle that will be split into arcs to be part of the toolpath later.
    """
    span_angle = 2 * math.pi
    return ArcData(
        origin,
        radius,
        None,
        None,
        0,
        span_angle,
        winding_dir,
        origin.buffer(radius).boundary,
        "",
    )


def create_arc(
    origin: Point,
    radius: float,
    start_angle: float,
    span_angle: float,
    winding_dir: ArcDir,
) -> Optional[ArcData]:
    """
    Generate a arc.

    Args:
        origin: Center of arc.
        radius: Radius of arc.
        start_angle: Angle from vertical. (Clockwise)
        span_angle: Angular length of arc.
    """
    if radius == 0:
        return None

    span_angle = min(span_angle, 2 * math.pi)
    span_angle = max(span_angle, -2 * math.pi)

    start_angle = start_angle % (2 * math.pi)

    line_up = LineString([origin, Point(origin.x, origin.y + radius * 2)])
    circle_path = origin.buffer(radius).boundary
    circle_path = split(circle_path, line_up)
    points = circle_path.geoms[1].coords[:] + circle_path.geoms[0].coords[:]
    circle_path = LineString(points)

    if abs(span_angle) == 2 * math.pi:
        return ArcData(
            origin,
            radius,
            Point(circle_path.coords[0]),
            Point(circle_path.coords[0]),
            start_angle,
            span_angle,
            winding_dir,
            circle_path,
            "",
        )

    # With shapely.affinity.rotate(...) -ive angles are clockwise.
    right_border = rotate(line_up, -span_angle, origin=origin, use_radians=True)

    if winding_dir == ArcDir.CCW:
        arc_path = split(circle_path, right_border).geoms[1]
        arc_path = LineString(arc_path.coords[::-1])
    else:
        arc_path = split(circle_path, right_border).geoms[0]

    arc_path = rotate(arc_path, -start_angle, origin=origin, use_radians=True)
    return ArcData(
        origin,
        radius,
        Point(arc_path.coords[0]),
        Point(arc_path.coords[-1]),
        start_angle,
        span_angle,
        winding_dir,
        arc_path,
        "",
    )


def create_arc_from_path(
    origin: Point,
    path: LineString,
    radius: float,
    winding_dir: Optional[ArcDir] = None,
    debug: str = None,
) -> ArcData:
    """
    Save data for the arc sections of the path.
    """
    start = Point(path.coords[0])
    end = Point(path.coords[-1])
    start_angle = None
    span_angle = None

    return ArcData(
        origin, radius, start, end, start_angle, span_angle, winding_dir, path, debug
    )


def mirror_arc(
    x_line: float, arc_data: ArcData, winding_dir: Optional[ArcDir] = None
) -> ArcData:
    """
    Mirror X axis of an arc about the origin point.
    """

    if winding_dir is None:
        assert (
            arc_data.winding_dir == ArcDir.CW
            and arc_data.span_angle is not None
            and arc_data.span_angle > 0
            or arc_data.winding_dir == ArcDir.CCW
            and arc_data.span_angle is not None
            and arc_data.span_angle < 0
        )

        if arc_data.winding_dir == ArcDir.CW:
            winding_dir = ArcDir.CCW
        else:
            winding_dir = ArcDir.CW
    else:
        if winding_dir == arc_data.winding_dir:
            return arc_data

    arc_path = LineString(
        [((2 * x_line - point[0]), point[1]) for point in arc_data.path.coords]
    )
    origin = Point(2 * x_line - arc_data.origin.x, arc_data.origin.y)

    return ArcData(
        origin,
        arc_data.radius,
        Point(arc_path.coords[0]),
        Point(arc_path.coords[-1]),
        (
            -arc_data.start_angle % (math.pi * 2)
            if arc_data.start_angle is not None
            else None
        ),
        -arc_data.span_angle if arc_data.span_angle is not None else None,
        winding_dir,
        arc_path,
        arc_data.debug,
    )


def complete_arc(arc_data: ArcData, winding_dir_: ArcDir = None) -> Optional[ArcData]:
    """
    Calculate start_angle, span_angle and radius.
    Fix start, end and path direction based on winding_dir.
    This is called a lot so any optimizations here save us time.
    Given some properties of an arc, calculate the others.
    """
    winding_dir = winding_dir_
    if winding_dir is None:
        winding_dir = arc_data.winding_dir
    if winding_dir is None or winding_dir == ArcDir.Closest:
        winding_dir = ArcDir.CW

    # Make copy of path since we may need to modify it.
    path = LineString(arc_data.path)
    if path.length == 0.0:
        return None

    start_coord = path.coords[0]
    end_coord = path.coords[-1]
    mid = path.interpolate(0.5, normalized=True)

    # Breaking these out once rather than separately inline later saves us ~7%
    # CPU time overall.
    org_x, org_y = arc_data.origin.xy
    start_x, start_y = start_coord
    mid_x, mid_y = mid.xy
    end_x, end_y = end_coord

    start_angle = math.atan2(start_x - org_x[0], start_y - org_y[0])
    end_angle = math.atan2(end_x - org_x[0], end_y - org_y[0])
    mid_angle = math.atan2(mid_x[0] - org_x[0], mid_y[0] - org_y[0])

    ds = (start_angle - mid_angle) % (2 * math.pi)
    de = (mid_angle - end_angle) % (2 * math.pi)
    if (ds > 0 and de > 0 and winding_dir == ArcDir.CCW) or (
        ds < 0 and de < 0 and winding_dir == ArcDir.CW
    ):
        # Needs reversed.
        path = LineString(path.coords[::-1])
        start_angle, end_angle = end_angle, start_angle
        start_coord, end_coord = end_coord, start_coord

    if winding_dir == ArcDir.CW:
        span_angle = (end_angle - start_angle) % (2 * math.pi)
    elif winding_dir == ArcDir.CCW:
        span_angle = (-(start_angle - end_angle) % (2 * math.pi)) - (2 * math.pi)

    if span_angle == 0.0:
        span_angle = 2 * math.pi

    radius = arc_data.radius or arc_data.origin.distance(Point(path.coords[0]))

    return ArcData(
        arc_data.origin,
        radius,
        Point(start_coord),
        Point(end_coord),
        start_angle % (2 * math.pi),
        span_angle,
        winding_dir,
        path,
        arc_data.debug,
    )


def arcs_from_circle_diff(
    circle: ArcData, already_cut: Polygon, debug: str|None = None
) -> List[ArcData]:
    """Return any sections of circle that do not overlap already_cut."""
    if not already_cut:
        return [circle]
    if circle is None:
        return None

    line_diff = circle.path.difference(already_cut)
    if not line_diff:
        return []
    if line_diff.geom_type == "MultiLineString":
        line_diff = linemerge(line_diff)
    if line_diff.geom_type != "MultiLineString":
        line_diff = MultiLineString([line_diff])

    arcs = []
    assert circle.radius is not None
    for arc in line_diff.geoms:
        arcs.append(
            create_arc_from_path(
                circle.origin,
                arc,
                circle.radius,
                winding_dir=circle.winding_dir,
                debug=debug,
            )
        )
    return arcs


def _colapse_dupe_points(line: LineString) -> Optional[LineString]:
    """
    Filter out duplicate points.
    TODO: Profile whether a .simplify(0) would be quicker?
    """
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


def split_line_by_poly(
    line: LineString, poly: Union[Polygon, MultiPolygon]
) -> MultiLineString:
    """
    split() sometimes fails if line shares a point with one of poly's rings.
    """

    if isinstance(poly, Polygon):
        poly = MultiPolygon([poly])
    rings = []
    for p in poly.geoms:
        rings.append(p.exterior)
        rings.extend(p.interiors)
    new_lines = []
    lines = [line]
    for ring in rings:
        for l in lines:
            try:
                split_line = split(l, LineString(ring))
            except (GeometryTypeError, TypeError, ValueError):
                split_line = MultiLineString([l])
            new_lines.extend(split_line.geoms)
        lines = new_lines
        new_lines = []

    # Check for gaps caused by line being co-linear to poly.
    last_new_line = None
    checked_lines = []
    for new_line in lines:
        if last_new_line is None:
            if line.coords[0] != new_line.coords[0]:
                checked_lines.append(LineString([line.coords[0], new_line.coords[0]]))
        else:
            if last_new_line.coords[-1] != new_line.coords[0]:
                checked_lines.append(
                    LineString([last_new_line.coords[-1], new_line.coords[0]])
                )
        checked_lines.append(new_line)
        last_new_line = new_line
    if last_new_line.coords[-1] != line.coords[-1]:
        checked_lines.append(LineString([last_new_line.coords[-1], line.coords[-1]]))

    return MultiLineString(checked_lines)


class BaseGeometry:
    # Area we have calculated arcs for. Calculated by appending full circles.
    calculated_area_total: Polygon
    # Area we have stored the toolpath for. Calculated by appending full circles.
    cut_area_total: Polygon

    starting_cut_area: Polygon

    def __init__(
        self,
        to_cut: Union[Polygon, MultiPolygon],
        step: float,
        winding_dir: ArcDir,
        already_cut: Polygon = None,
    ) -> None:
        self.polygon: Union[Polygon, MultiPolygon] = to_cut
        self.step: float = step
        self.winding_dir: ArcDir = winding_dir
        if already_cut is None:
            already_cut = Polygon()
        self.starting_cut_area = already_cut
        self.path: List[Union[ArcData, LineData]] = []
        self.pending_arc_queues: List[List[ArcData]] = []
        self.last_arc: Optional[ArcData] = None

        self.calculated_area_total = self.starting_cut_area
        self.cut_area_total = Polygon(self.starting_cut_area)
        ## XM : assert self.calculated_area_total is not self.cut_area_total

        self._filter_input_geometry()
        self.dilated_starting_polygon = self.polygon.buffer(self.step / 10)

    def _filter_input_geometry(self) -> None:
        """Remove any tiny polygons from a MultiPolygon."""
        min_area = (self.step / 20) ** 2

        if self.polygon.geom_type != "MultiPolygon":
            self.polygon = MultiPolygon([self.polygon])

        self.polygon = MultiPolygon(
            [
                poly
                for poly in self.polygon.geoms
                if poly.buffer(-self.step / 20).area > min_area
            ]
        )

    def _flush_arc_queues(self) -> None:
        while self.pending_arc_queues:
            to_process = self.pending_arc_queues.pop(0)
            self._arcs_to_path(to_process)

    def _check_queue_overlap(self, arc: ArcData, queue_index: int) -> bool:
        """
        Arcs should only be added if the area inside them has been cleared.
        This checks for overlaps between the specified arc and those that are
        to be cut /after/ it.
        Returns:
            True: If no overlap occurs.
            False: If the proposed arc is blocked for this queue by as yet uncut arcs.
        """
        dilated_arc = arc.path.buffer(self.step)
        for queue in self.pending_arc_queues[queue_index + 1 :]:
            for existing_arc in queue:
                if existing_arc.path.intersects(dilated_arc):
                    return False
        return True

    def _queue_arcs(self, new_arcs: List[ArcData]) -> None:
        """
        When an arc intersects with an area that has already been cut the arc may
        get split into multiple pieces.
        When we cone to join the arcs we want to join the "left" arcs to each other
        and the "right" arcs to each other. (There may be more than 2 sets as well.)
        To do this we need to store arcs in separate queues. Each queue contains
        arcs that should be joined to each other.
        """

        # Need to put each arc in the queue with nearest predecessor.
        modified_queues_indexes = set()

        if len(new_arcs) == 1 and len(self.pending_arc_queues) == 1:
            # Optimization to save expensive repeated distance calculations.
            # Only a single queue and a single arc so we don't need complicated
            # queues.
            # Just add the arc to the single queue.
            # Since there are no other queues depending on our remaining one,
            # it is safe to drain it,
            self.pending_arc_queues[0].append(new_arcs[0])
            to_process = self.pending_arc_queues.pop(0)
            self._arcs_to_path(to_process)
            return
        else:
            closest_queue: Optional[List[ArcData]]
            for arc in new_arcs:
                closest_queue = None
                closest_queue_index = None
                closest_dist = self.step
                for queue_index, queue in enumerate(self.pending_arc_queues):
                    if self.winding_dir == ArcDir.Closest:
                        combined_dist = 1.0
                        seperate_dist = 0.0
                    else:
                        assert arc.start is not None
                        assert queue[-1].start is not None
                        assert queue[-1].end is not None

                        seperate_dist = queue[-1].start.distance(
                            queue[-1].end
                        ) + arc.start.distance(arc.end)
                        combined_dist = queue[-1].start.distance(arc.end) + queue[
                            -1
                        ].end.distance(arc.start)

                    seperation = arc.path.distance(queue[-1].path)
                    if seperation < closest_dist or combined_dist < seperate_dist:
                        if self._check_queue_overlap(arc, queue_index):
                            closest_dist = seperation
                            closest_queue = queue
                            closest_queue_index = queue_index
                if closest_queue is None:
                    # Not close to any predecessor. Create new queue.
                    closest_queue = []
                    closest_queue_index = len(self.pending_arc_queues)
                    self.pending_arc_queues.append(closest_queue)
                closest_queue.append(arc)
                modified_queues_indexes.add(closest_queue_index)
                assert closest_queue_index is not None
                assert closest_queue is self.pending_arc_queues[closest_queue_index]
                assert arc in closest_queue

        # Queues need processed in the order they were created: FIFO.
        # It is only safe to process the oldest queue (index: 0) as any younger
        # queue may be a child of it.
        # TODO: If we really wanted to, whenever there are any un-modified queues,
        # we could process the contents of all the older queues even though they
        # are still being appended to before processing the un-modifies queue(s).
        if modified_queues_indexes and 0 not in modified_queues_indexes:
            to_process = self.pending_arc_queues.pop(0)
            self._arcs_to_path(to_process)

    def _arcs_to_path(self, arcs: List[ArcData]) -> None:
        """
        Process list list of arcs, calculate tool path to join one to the next
        and apply them to the self.path parameter.

        Note: This function modifies the arcs parameter in place.
        """
        while arcs:
            arc = arcs.pop(0)
            if arc is None:
                continue

            winding_dir = self.winding_dir
            last_arc = self.last_arc
            if winding_dir == ArcDir.Closest:
                if last_arc is None:
                    winding_dir = ArcDir.CW
                else:
                    # TODO: We could improve this: Rather that taking the opposite
                    # of the last arc, we could work out the closest end based on
                    # the last drawn arc.
                    if last_arc.winding_dir == ArcDir.CCW:
                        winding_dir = ArcDir.CW
                    else:
                        winding_dir = ArcDir.CCW

                    assert last_arc.start is not None
                    assert last_arc.end is not None

                    if last_arc.end.distance(arc.start) < last_arc.end.distance(
                        arc.end
                    ):
                        winding_dir = ArcDir.CW
                    if last_arc.start.distance(arc.end) < last_arc.end.distance(
                        arc.end
                    ):
                        winding_dir = ArcDir.CW

                # TODO: Just reversing arc.path, arc.span_angle and arc.winding_dir
                # would be quicker than calling complete_arc(...).
                arc_ = complete_arc(arc, winding_dir)
                if arc_ is None:
                    continue
                arc = arc_

            assert arc.path.length > 0
            assert len(arc.path.coords) >= 2
            assert arc.span_angle != 0

            if last_arc is not None:
                self.path += self.join_arcs(arc)
            self.path.append(arc)
            self.last_arc = arc

    def join_arcs(self, next_arc: ArcData) -> List[LineData]:
        """
        Generate CAM tool path to join the end of one arc to the beginning of the next.
        Also tracks what geometry has actually been cut (as opposed to just planned).
        """
        assert self.last_arc

        # Add a section of the full circle to the cut area.
        arc_poly = Polygon(list(next_arc.path.coords) + [next_arc.origin]).buffer(
            self.step / 20
        )
        to_cut_area_total = self.cut_area_total.union(arc_poly)

        lines = []
        path = LineString([self.last_arc.end, next_arc.start])
        inside_pocket = path.covered_by(
            self.dilated_starting_polygon
        ) or path.covered_by(to_cut_area_total)

        if inside_pocket:
            # Whole path is inside pocket.
            if path.length <= self.step:
                return [
                    LineData(
                        Point(path.coords[0]),
                        Point(path.coords[-1]),
                        path,
                        MoveStyle.CUT,
                    )
                ]

            split_for_last = path.interpolate(-self.step)
            last_line = LineData(
                Point(split_for_last),
                Point(next_arc.start),
                LineString([split_for_last, next_arc.start]),
                MoveStyle.CUT,
            )

            remaining_path = LineString([self.last_arc.end, split_for_last])

            split_path = split_line_by_poly(remaining_path, self.cut_area_total)

            for part in split_path.geoms:
                assert part.geom_type == "LineString"
                assert len(part.coords) == 2

                move_style = MoveStyle.CUT
                if (
                    part.intersection(self.cut_area_total).length
                    > part.length - self.step / 20
                ):
                    # if part.covered_by(self.cut_area_total):
                    move_style = MoveStyle.RAPID_INSIDE

                line = LineData(
                    Point(part.coords[0]),
                    Point(part.coords[-1]),
                    part,
                    move_style,
                )

                if line.path.length > SHORTEST_RAPID:
                    lines.append(line)
            lines.append(last_line)
        else:
            # Path is not entirely inside pocket or crosses uncut area.
            move_style = MoveStyle.RAPID_OUTSIDE
            line = LineData(
                self.last_arc.end,
                next_arc.start,
                path,
                move_style,
            )
            if line.path.length > SHORTEST_RAPID:
                lines.append(line)

        self.cut_area_total = to_cut_area_total

        return lines

    def _split_arcs(self, full_arcs: List[ArcData]) -> List[ArcData]:
        """
        When an arcs pass through an already cut area, it should be trimmed to
        remove the already cut section.
        It's important to keep the sequence of the order of the resulting sub arcs
        the same as the originals so the final path can pass through them in order.
        """
        calculated_area_total = self.calculated_area_total
        split_arcs = []
        for full_arc in full_arcs:
            new_arcs = arcs_from_circle_diff(full_arc, calculated_area_total)
            if not new_arcs:
                continue

            new_arcs = list(
                filter(
                    None,
                    [
                        complete_arc(new_arc, new_arc.winding_dir)
                        for new_arc in new_arcs
                        if new_arc.path.length
                    ],
                )
            )

            arc_set = set()
            for new_arc_index, new_arc in enumerate(new_arcs):
                arc_set.add((full_arc.path.project(new_arc.start), new_arc_index))

            for _, new_arc_index in sorted(arc_set):
                split_arcs.append(new_arcs[new_arc_index])

        return split_arcs


class Pocket(BaseGeometry):
    """
    A CAM library to generate a HSM "peeling" pocketing toolpath.
    """

    start_point: Point
    max_starting_radius: float
    starting_angle: Optional[float] = None
    last_arc: Optional[ArcData]
    last_circle: Optional[ArcData]
    debug: bool = False

    def __init__(
        self,
        to_cut: Polygon,
        step: float,
        winding_dir: ArcDir,
        already_cut: Polygon = None,
        generate: bool = False,
        voronoi: Optional[VoronoiCenters] = None,
        starting_point_tactic: StartPointTactic = StartPointTactic.WIDEST,
        starting_point: Point = None,
        starting_radius: float = None,
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

        clean_multipolygon(to_cut)
        clean_multipolygon(complete_pocket)
        clean_multipolygon(already_cut)

        self.starting_cut_area = already_cut
        self.starting_radius = starting_radius
        self.generate = generate
        self.debug = debug

        # Calculate voronoi diagram for finding points equidistant between part edges.
        if voronoi is None:
            if starting_point is not None:
                voronoi = VoronoiCenters(complete_pocket, starting_point=starting_point)
            elif starting_point_tactic == StartPointTactic.WIDEST:
                voronoi = start_point_widest(
                    self.starting_radius, step, complete_pocket, already_cut
                )
            elif starting_point_tactic == StartPointTactic.PERIMETER:
                voronoi = start_point_perimeter(
                    self.starting_radius or step, complete_pocket, already_cut
                )

            assert voronoi is not None
        self.voronoi = voronoi

        # Calculate entry hole settings.
        self.max_starting_radius = voronoi.max_starting_radius
        if starting_radius and self.max_starting_radius < starting_radius:
            print(
                f"Warning: Starting radius of {starting_radius} overlaps boundaries "
                f"at {voronoi.start_point}"
            )
            print(
                f" Largest possible at this location: {round(self.max_starting_radius, 3)}"
            )
        if self.starting_radius is not None:
            radius = min(self.starting_radius, self.max_starting_radius)
            start_circle = voronoi.start_point.buffer(radius)
            already_cut = already_cut.union(start_circle)

        super().__init__(to_cut, step, winding_dir, already_cut=already_cut)

        self._reset()
        self.calculate_path()

    def _reset(self) -> None:
        """Cleanup and/or initialise everything."""

        self.start_point: Point = self.voronoi.start_point
        self.start_radius: float = self.voronoi.start_distance or 0

        self.arc_fail_count: int = 0
        self.path_fail_count: int = 0
        self.loop_count: int = 0

        self.visited_edges: Set[int] = set()
        self.open_paths: Dict[int, Tuple[float, float]] = {}

        self.path_len_progress: float = 0.0
        self.path_len_total: float = 0.0
        for edge in self.voronoi.edges.values():
            self.path_len_total += edge.length

        # Used to detect when an arc is too close to the edge to be worthwhile.
        self.dilated_polygon_boundaries = []
        multi = self.polygon
        if multi.geom_type != "MultiPolygon":
            multi = MultiPolygon([multi])
        for poly in multi.geoms:
            for ring in [poly.exterior] + list(poly.interiors):
                self.dilated_polygon_boundaries.append(
                    ring.buffer(self.step * SKIP_EDGE_ARCS)
                )

        # Generate first circle from which other arcs expand.
        entry_circle = EntryCircle(
            self.polygon,
            self.start_point,
            self.start_radius,
            self.step,
            self.winding_dir,
            already_cut=self.calculated_area_total,
            path=self.path,
        )
        entry_circle.spiral()
        entry_circle.circle()

        if self.starting_radius is not None:
            radius = min(self.starting_radius, self.max_starting_radius)
            if (
                self.path
                and self.start_point.buffer(radius).distance(self.path[0].start)
                < self.step / 20
            ):
                assert self.path[0].start
                dx = self.path[0].start.x - self.start_point.x
                dy = self.path[0].start.y - self.start_point.y
                self.starting_angle = math.atan2(dx, dy)

        self.last_arc = entry_circle.last_arc

        self.last_circle: Optional[ArcData] = create_circle(
            self.start_point, self.start_radius
        )
        self.calculated_area_total = self.calculated_area_total.union(
            Polygon(self.last_circle.path)
        )

    def calculate_path(self) -> None:
        """Reset path and restart from beginning."""
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
                    # "cut_progress": self.calculated_area_total,
                },
                voronoi=self.voronoi,
                path=self.path,
            )

    def _choose_next_path(
        self, current_pos: Optional[Tuple[float, float]] = None
    ) -> Optional[Tuple[float, float]]:
        """
        Choose a vertex with an un-traveled voronoi edge leading from it.

        Returns:
            A vertex that has un-traveled edges leading from it.
        """
        # Cleanup.
        for edge_i in self.visited_edges:
            if edge_i in self.open_paths:
                self.open_paths.pop(edge_i)

        shortest = self.voronoi.max_dist + 1
        closest_vertex: Optional[Tuple[float, float]] = None
        closest_edge: Optional[int] = None
        for edge_i, vertex in self.open_paths.items():
            if current_pos:
                dist = Point(vertex).distance(Point(current_pos))
            else:
                dist = 0

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
            self.open_paths.pop(closest_edge)

        self.last_circle = None
        return closest_vertex

    @classmethod
    def _extrapolate_line(cls, extra: float, line: LineString) -> LineString:
        """
        Extend a line at both ends in the same direction it points.
        """
        coord_0, coord_1 = line.coords[:2]
        coord_m2, coord_m1 = line.coords[-2:]
        ratio_begin = extra / LineString([coord_0, coord_1]).length
        ratio_end = extra / LineString([coord_m2, coord_m1]).length
        coord_begin = Point(
            coord_0[0] + (coord_0[0] - coord_1[0]) * ratio_begin,
            coord_0[1] + (coord_0[1] - coord_1[1]) * ratio_begin,
        )
        coord_end = Point(
            coord_m1[0] + (coord_m1[0] - coord_m2[0]) * ratio_end,
            coord_m1[1] + (coord_m1[1] - coord_m2[1]) * ratio_end,
        )
        return LineString([coord_begin] + list(line.coords) + [coord_end])

    @classmethod
    def _converge(cls, kp: float) -> Generator[float, Tuple[float, float], None]:
        """
        Algorithm used for recursively estimating the position of the best fit arc.

        Arguments:
            kp: Proportional multiplier.
        Yields:
            Arguments:
                target: Target step size.
                current: step size resulting from the previous iteration result.
            next distance.
        Returns:
            Never exits Yield loop.
        """
        error: float = 0.0
        value: float = 0.0

        while True:
            target, current = yield value

            error = target - current
            prportional = kp * error
            value = prportional

    def _arc_at_distance(
        self, distance: float, voronoi_edge: LineString
    ) -> Tuple[Point, float]:
        """
        Calculate the center point and radius of the largest arc that fits at a
        set distance along a voronoi edge.
        """
        pos = voronoi_edge.interpolate(distance)
        radius = self.voronoi.distance_from_geom(pos)

        return (pos, radius)

    def _furthest_spacing_arcs(
        self, arcs: List[ArcData], last_circle: ArcData
    ) -> float:
        """
        Calculate maximum step_over between 2 arcs.
        """
        # return self._furthest_spacing_shapely(arcs, last_circle.path)
        spacing = -self.voronoi.max_dist

        for arc in arcs:
            spacing = max(
                spacing,
                last_circle.origin.hausdorff_distance(arc.path) - last_circle.radius,
            )

            # for index in range(0, len(arc.path.coords), 1):
            #    coord = arc.path.coords[index]
            #    spacing = max(spacing,
            #            Point(coord).distance(last_circle.origin) - last_circle.radius)

        return abs(spacing)

    @classmethod
    def _furthest_spacing_shapely(
        cls, arcs: List[ArcData], previous: LineString
    ) -> float:
        """
        Calculate maximum step_over between 2 arcs.

        TODO: Current implementation is expensive. Not sure how shapely's distance
        method works but it is likely "O(N)", making this implementation N^2.
        We can likely reduce that to O(N*log(N)) with a binary search.

        Arguments:
            arcs: The new arcs.
            previous: The previous cut path geometry we are testing the arks against.

        Returns:
            The step distance.
        """
        spacing = -1.0
        polygon = previous
        for arc in arcs:
            if not arc.path:
                continue

            # This is expensive but yields good results.
            # Probably want to do a binary search version?

            for index in range(0, len(arc.path.coords), 1):
                coord = arc.path.coords[index]
                # spacing = max(spacing, Point(coord).distance(polygon))
                spacing = max(spacing, polygon.distance(Point(coord)))

        return spacing

    def _calculate_arc(
        self,
        voronoi_edge: LineString,
        start_distance: float,
        min_distance: float,
    ) -> Tuple[float, List[ArcData]]:
        """
        Calculate the arc that best fits within the path geometry.

        A given point on the voronoi_edge is equidistant between the edges of the
        desired cut path. We can calculate this distance and it forms the radius
        of an arc touching the cut path edges.
        We need the furthest point on that arc to be desired_step distance away from
        the previous arc. It is hard to calculate a point on the voronoi_edge that
        results in the correct spacing between the new and previous arc.

        The constraints for the new arc are:
        1) The arc must go through the point on the voronoi edge desired_step
          distance from the previous arc's intersection with the voronoi edge.
        2) The arc must be a tangent to the edge of the cut pocket.
          Or put another way: The distance from the center of the arc to the edge
          of the cut pocket should be the same as the distance from the center of
          the arc to the point described in 1).

        Rather than work out the new arc centre position with maths, it is quicker
        and easier to use a binary search, moving the proposed centre repeatedly
        and seeing if the arc fits.

        Arguments:
            voronoi_edge: The line of mid-way points between the edges of desired
              cut path.
            start_distance: The distance along voronoi_edge to start trying to
              find an arc that fits.
            min_distance: Do not return arcs below this distance; The algorithm
              is confused and traveling backwards.
        Returns:
            A tuple containing:
                1. Distance along voronoi edge of the final arc.
                2. A collection of ArcData objects containing relevant information
                about the arcs generated with an origin the specified distance
                allong the voronoi edge.
        """
        # A generator to converge on desired spacing.
        # converge = self._converge(0.75)
        converge = self._converge(0.76)
        converge.send(None)  # type: ignore

        coverage_algos = [
            # self._converge(0.75),
            self._converge(0.76),
            self._converge(0.74),
            self._converge(0.78),
            self._converge(0.72),
            self._converge(0.7),
            self._converge(0.8),
        ]

        color_overide = None

        desired_step = min(self.step, (voronoi_edge.length - start_distance))

        distance = start_distance + desired_step

        count: int = 0
        circle: Optional[ArcData] = None
        arcs: List[ArcData] = []
        progress: float = 0.0
        best_progress: float = 0.0
        best_distance: float = 0.0
        dist_offset: int = 100000
        corner_zoom = CORNER_ZOOM * self.step

        # Extrapolate line beyond it's actual distance to give the algorithm
        # room to overshoot while converging on an optimal position for the new arc.
        edge_extended: LineString = self._extrapolate_line(dist_offset, voronoi_edge)
        assert (
            abs(edge_extended.length - (voronoi_edge.length + 2 * dist_offset)) < 0.0001
        )

        assert self.calculated_area_total
        assert self.calculated_area_total.is_valid

        # Loop multiple times, trying to converge on a distance along the voronoi
        # edge that provides the correct step size.
        while count <= ITERATION_COUNT:
            count += 1

            # Propose an arc.
            pos, radius = self._arc_at_distance(distance + dist_offset, edge_extended)
            circle = create_circle(pos, radius, self.winding_dir)

            # Compare proposed arc to cut area.
            # We are only interested in sections that have not been cut yet.
            arcs = self._split_arcs([circle])
            if not arcs:
                # arc is entirely hidden by previous cut geometry.

                if best_progress > 0:
                    # Has made some progress.
                    count = ITERATION_COUNT
                    color_overide = "orange"
                    break

                # Has not found any useful arc yet.
                # Don't record it as an arc that needs drawn.
                self.last_circle = circle
                return (distance, [])

            # Progress is measured as the furthest point the proposed arc is
            # from the previous one. We are aiming for proposed == desired_step.
            if self.last_circle:
                progress = self._furthest_spacing_arcs(arcs, self.last_circle)
            else:
                progress = self._furthest_spacing_shapely(
                    arcs, self.calculated_area_total
                )

            desired_step = min(self.step, (voronoi_edge.length - start_distance))
            if radius < corner_zoom:
                # Limit step size as the arc radius gets very small.
                multiplier = (corner_zoom - radius) / corner_zoom
                desired_step = self.step * (1 - CORNER_ZOOM_EFFECT * multiplier)

            if abs(desired_step - progress) < abs(desired_step - best_progress):
                # Better fit.
                best_progress = progress
                best_distance = distance

                if abs(desired_step - progress) < desired_step / 20:
                    # Good enough fit.
                    best_progress = progress
                    best_distance = distance
                    break

            modifier = converge.send((desired_step, progress))
            distance += modifier

        if count == ITERATION_COUNT:
            color_overide = "red"
            if distance < min_distance:
                # Moving the wrong way along the voronoi edge.
                # Only happens when we've been to the end of an edge already.
                return (voronoi_edge.length, [])

        if best_distance > voronoi_edge.length:
            best_distance = voronoi_edge.length

        if (
            distance != best_distance
            or progress != best_progress
            or color_overide is not None
        ):
            distance = best_distance
            progress = best_progress
            pos, radius = self._arc_at_distance(distance + dist_offset, edge_extended)
            circle = create_circle(Point(pos), radius, self.winding_dir)
            arcs = self._split_arcs([circle])

        if count == ITERATION_COUNT and self.debug:
            # Log some debug data.
            distance_remain = voronoi_edge.length - distance
            self.arc_fail_count += 1
            log(
                "\tDid not find an arc that fits. Spacing/Desired: "
                f"{round(progress, 3)}/{desired_step}"
                "\tdistance remaining: "
                f"{round(distance_remain, 3)}"
            )

        self.loop_count += count

        assert circle is not None
        self.last_circle = circle
        self.calculated_area_total = self.calculated_area_total.union(
            Polygon(circle.path)
        )

        filtered_arcs = []
        for arc in arcs:
            if self._filter_arc(arc):
                filtered_arcs.append(arc)

        return (distance, filtered_arcs)

    def _join_voronoi_branches(self, start_vertex: Tuple[float, float]) -> LineString:
        """
        Walk a section of the voronoi edge tree, creating a combined edge as we
        go.

        Returns:
            A LineString object of the combined edges.
        """
        vertex = start_vertex

        line_coords: List[Tuple[float, float]] = []

        while True:
            branches = self.voronoi.vertex_to_edges[vertex]
            candidate = None
            longest = 0.0
            for branch in branches:
                if branch not in self.visited_edges:
                    self.open_paths[branch] = vertex
                    length = self.voronoi.edges[branch].length
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
            edge_coords = self.voronoi.edges[candidate].coords

            if not line_coords:
                line_coords = edge_coords
                if start_vertex != line_coords[0]:
                    line_coords = line_coords[::-1]
            else:
                if line_coords[-1] == edge_coords[-1]:
                    edge_coords = edge_coords[::-1]
                assert line_coords[0] == start_vertex
                assert line_coords[-1] == edge_coords[0]
                line_coords = list(line_coords) + list(edge_coords)

            vertex = line_coords[-1]

        line = LineString(line_coords)

        return _colapse_dupe_points(line)

    def get_arcs(self, timeslice: int = 0):
        """
        A generator method to create the path.

        Class instance properties:
            self.generate: bool: Whether or not to yield.
                False: Do not yield. Generate all data in one shot.
                True: Yield an estimated ratio of path completion.

        Arguments:
            timeslice: int: How long to generate arcs for before yielding (ms).
        """
        start_time = round(time.time() * 1000)  # ms

        start_vertex: Optional[Tuple[float, float]] = self.start_point.coords[0]
        while start_vertex is not None:
            # This outer loop iterates through the voronoi vertexes, looking for
            # a voronoi edge that has not yet had arcs calculated for it.
            combined_edge = self._join_voronoi_branches(start_vertex)
            if not combined_edge:
                start_vertex = self._choose_next_path()
                continue

            dist = 0.0
            best_dist = dist
            stuck_count = int(combined_edge.length * 10 / self.step + 10)
            while abs(dist - combined_edge.length) > self.step / 20 and stuck_count > 0:
                # This inner loop travels along a voronoi edge, trying to fit arcs
                # that are the correct distance apart.
                stuck_count -= 1
                dist, new_arcs = self._calculate_arc(combined_edge, dist, best_dist)

                self.path_len_progress -= best_dist
                self.path_len_progress += dist

                if dist < best_dist and False:
                    # Getting worse not better or staying the same.
                    # This can happen legitimately but is an indication the algorthm
                    # may be stuck.
                    stuck_count = int(stuck_count / 2)
                else:
                    best_dist = dist
                self._queue_arcs(new_arcs)

                if timeslice >= 0 and self.generate:
                    now = round(time.time() * 1000)  # (ms)
                    if start_time + timeslice < now:
                        yield min(0.999, self.path_len_progress / self.path_len_total)
                        start_time = round(time.time() * 1000)  # (ms)

            if stuck_count <= 0:
                print(f"stuck: {round(dist, 2)} / {round(combined_edge.length, 2)}")
                self.path_fail_count += 1

            start_vertex = self._choose_next_path(combined_edge.coords[-1])

            self._flush_arc_queues()

        if timeslice and self.generate:
            yield 1.0

        assert not self.open_paths
        log(f"loop_count: {self.loop_count}")
        log(f"arc_fail_count: {self.arc_fail_count}")
        log(f"len(path): {len(self.path)}")
        log(f"path_fail_count: {self.path_fail_count}")

        self.done_generating()

    def _filter_arc(self, arc: ArcData) -> Optional[ArcData]:
        """
        Remove any arc that is very close to the edge of the part in it's entirety.
        """
        if len(arc.path.coords) < 3:
            return None

        if arc.path.length <= self.step / 20:
            # Arc too short to care about.
            return None

        if not arc.path.intersects(self.polygon):
            return None

        poly_arc = Polygon(arc.path)
        for ring in self.dilated_polygon_boundaries:
            if ring.contains(poly_arc):
                return None

        return arc

    def _start_point_perimeter(
        self, polygons: MultiPolygon, already_cut: Polygon, step: float
    ) -> VoronoiCenters:
        """
        Recalculate the start point to be inside the cut area, adjacent to the perimeter.
        """
        starting_radius = self.starting_radius or step
        voronoi = VoronoiCenters(polygons, preserve_edge=True)

        perimiter_point = voronoi.start_point
        assert perimiter_point is not None
        voronoi_edge_index = voronoi.vertex_to_edges[perimiter_point.coords[0]]
        assert len(voronoi_edge_index) == 1
        voronoi_edge = voronoi.edges[voronoi_edge_index[0]]
        cut_edge_section = already_cut.intersection(voronoi_edge)
        if cut_edge_section.length > starting_radius * 2:
            new_start_point = cut_edge_section.interpolate(0.5, normalized=True)

            voronoi = VoronoiCenters(polygons, starting_point=new_start_point)
        else:
            # Can't fit starting_radius here.
            # Look for widest point in already_cut area.
            cut_voronoi = VoronoiCenters(already_cut, preserve_widest=True)
            voronoi = VoronoiCenters(polygons, starting_point=cut_voronoi.start_point)
            del cut_voronoi

        return voronoi


class EntryCircle(BaseGeometry):
    center: Point
    radius: float
    start_angle: float
    path: List[Union[ArcData, LineData]]

    def __init__(
        self,
        to_cut: Polygon,
        center: Point,
        radius: float,
        step: float,
        winding_dir: ArcDir,
        start_angle: float = 0,
        already_cut: Optional[Polygon] = None,
        path: Optional[List[Union[ArcData, LineData]]] = None,
    ):
        super().__init__(to_cut, step, winding_dir, already_cut)

        self.center = center
        self.radius = radius
        self.start_angle = start_angle

        if path is None:
            path = []
        self.path = path

    def spiral(self):
        loop: float = 0.25
        offset: List[float] = [0.0, 0.0]
        new_arcs = []
        mask = self.center.buffer(self.radius)
        not_done = True
        while loop * self.step <= self.radius and not_done:
            orientation = round(loop * 4) % 4
            if orientation == 0:
                start_angle = 0
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
                raise

            section_center = Point(self.center.x + offset[0], self.center.y + offset[1])
            new_arc = create_arc(
                section_center, section_radius, start_angle, math.pi / 2, ArcDir.CW
            )

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

                new_arc = create_arc_from_path(
                    new_arc.origin, masked_arc, new_arc.radius, ArcDir.CW
                )
                new_arc = complete_arc(new_arc, new_arc.winding_dir)

                not_done = False

            if self.winding_dir == ArcDir.CCW:
                new_arc = mirror_arc(self.center.x, new_arc)

            new_arcs.append(new_arc)
            loop += 0.25  # 1/4 turn.

        # self._queue_arcs(new_arcs)

        sorted_arcs = self._split_arcs(new_arcs)
        sorted_arcs = [complete_arc(sorted_arc) for sorted_arc in sorted_arcs]
        self._queue_arcs(sorted_arcs)

        self._flush_arc_queues()

    def circle(self):
        if self.winding_dir == ArcDir.CCW:
            angle = -math.pi * 1.99999
        else:
            angle = math.pi * 1.99999

        new_arc = create_arc(self.center, self.radius, 0, angle, self.winding_dir)
        sorted_arcs = self._split_arcs([new_arc])
        sorted_arcs = [complete_arc(sorted_arc) for sorted_arc in sorted_arcs]
        self._queue_arcs(sorted_arcs)
        self._flush_arc_queues()
