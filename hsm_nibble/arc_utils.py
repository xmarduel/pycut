"""
Arc and toolpath data types, and free utility functions for creating and
manipulating arcs.

Types defined here (ArcData, LineData, ArcDir, MoveStyle, StartPointTactic)
are imported by geometry.py so that arc_utils.py remains a leaf module with
no project-internal imports.
"""

from typing import NamedTuple

from enum import Enum
import math

import shapely  # type: ignore
from shapely.affinity import rotate  # type: ignore
from shapely.geometry import LineString, MultiLineString, Point, Polygon  # type: ignore
from shapely.ops import linemerge, split  # type: ignore


# ---------------------------------------------------------------------------
# Enums and NamedTuples
# ---------------------------------------------------------------------------

class ArcDir(Enum):
    CW = 0
    CCW = 1
    CLOSEST = 2

class MoveStyle(Enum):
    RAPID_OUTSIDE = 0
    RAPID_INSIDE = 1
    CUT = 2

class StartPointTactic(Enum):
    PERIMETER = 0  # Starting point hint for outer peel. On the outer perimeter.
    WIDEST = 1     # Starting point hint for inner pockets.

'''
ArcData = NamedTuple("ArcData", [
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
    ("debug", Optional[str])
])
'''

class ArcData(NamedTuple):
    origin: Point
    radius: float | None
    start: Point | None
    end: Point | None
    start_angle: float | None
    span_angle: float | None
    winding_dir: ArcDir | None
    path: LineString
    debug: str | None

'''
LineData = NamedTuple("LineData", [
    ("start", Point),
    ("end", Point),
    ("path", LineString),
    ("move_style", MoveStyle),
])
'''

class LineData(NamedTuple):
    start: Point
    end: Point
    path: LineString
    move_style: MoveStyle


# ---------------------------------------------------------------------------
# Arc construction
# ---------------------------------------------------------------------------

def create_circle(origin: Point, radius: float, winding_dir: ArcDir | None = None) -> ArcData:
    """
    Generate a circle that will be split into arcs to be part of the toolpath later.
    """
    span_angle = 2 * math.pi
    return ArcData(
        origin, radius, None, None, 0, span_angle, winding_dir, origin.buffer(radius).boundary, "")


def create_arc(
        origin: Point,
        radius: float,
        start_angle: float,
        span_angle: float,
        winding_dir: ArcDir) -> ArcData | None:
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
    circle_path = shapely.remove_repeated_points(LineString(points))

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
                "")

    # With shapely.affinity.rotate(...) -ive angles are clockwise.
    right_border = rotate(line_up, -span_angle, origin=origin, use_radians=True)

    if winding_dir == ArcDir.CCW:
        arc_path = split(circle_path, right_border).geoms[1]
        arc_path = LineString(arc_path.coords[::-1])
    else:
        arc_path = split(circle_path, right_border).geoms[0]

    arc_path = shapely.remove_repeated_points(
        rotate(arc_path, -start_angle, origin=origin, use_radians=True))
    return ArcData(
            origin,
            radius,
            Point(arc_path.coords[0]),
            Point(arc_path.coords[-1]),
            start_angle,
            span_angle,
            winding_dir,
            arc_path,
            "")


def create_arc_from_path(
        origin: Point,
        path: LineString,
        radius: float,
        winding_dir: ArcDir | None = None,
        debug: str | None = None
) -> ArcData:
    """
    Save data for the arc sections of the path.
    """
    path = shapely.remove_repeated_points(path)
    start = Point(path.coords[0])
    end = Point(path.coords[-1])
    start_angle = None
    span_angle = None

    return ArcData(
            origin,
            radius,
            start,
            end,
            start_angle,
            span_angle,
            winding_dir,
            path,
            debug)


def mirror_arc(
        x_line: float,
        arc_data: ArcData,
        winding_dir: ArcDir | None = None
        ) -> ArcData:
    """
    Mirror X axis of an arc about the origin point.
    """

    if winding_dir is None:
        assert (arc_data.winding_dir == ArcDir.CW and
                arc_data.span_angle is not None and
                arc_data.span_angle > 0 or
                arc_data.winding_dir == ArcDir.CCW and
                arc_data.span_angle is not None and
                arc_data.span_angle < 0)

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
            -arc_data.start_angle % (math.pi * 2) if arc_data.start_angle is not None else None,
            -arc_data.span_angle if arc_data.span_angle is not None else None,
            winding_dir,
            arc_path,
            arc_data.debug)


def complete_arc(
        arc_data: ArcData,
        winding_dir_: ArcDir | None = None
        ) -> ArcData | None:
    """
    Calculate start_angle, span_angle and radius.
    Fix start, end and path direction based on winding_dir.
    This is called a lot so any optimizations here save us time.
    Given some properties of an arc, calculate the others.
    """
    winding_dir = winding_dir_
    if winding_dir is None:
        winding_dir = arc_data.winding_dir
    if winding_dir is None or winding_dir == ArcDir.CLOSEST:
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
    if ((ds > 0 and de > 0 and winding_dir == ArcDir.CCW) or
            (ds < 0 and de < 0 and winding_dir == ArcDir.CW)):
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
            arc_data.debug)


# ---------------------------------------------------------------------------
# Arc set operations
# ---------------------------------------------------------------------------

def arcs_from_circle_diff(
        circle: ArcData,
        already_cut: Polygon,
        debug: str | None = None
        ) -> list[ArcData]:
    """ Return any sections of circle that do not overlap already_cut. """
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
        arcs.append(create_arc_from_path(
            circle.origin, arc, circle.radius, winding_dir=circle.winding_dir, debug=debug))
    return arcs


def split_arcs(full_arcs: list[ArcData], calculated_area: Polygon) -> list[ArcData]:
    """
    When arcs pass through an already cut area, trim them to remove the
    already cut section.
    Keeps the sequence order of the resulting sub-arcs the same as the
    originals so the final path can pass through them in order.
    """
    result = []
    for full_arc in full_arcs:
        new_arcs = arcs_from_circle_diff(full_arc, calculated_area)
        if not new_arcs:
            continue

        new_arcs = list(filter(
            None, [complete_arc(new_arc, new_arc.winding_dir)
                for new_arc in new_arcs if new_arc.path.length]
            ))

        arc_set = set()
        for new_arc_index, new_arc in enumerate(new_arcs):
            arc_set.add((full_arc.path.project(new_arc.start), new_arc_index))

        for _, new_arc_index in sorted(arc_set):
            result.append(new_arcs[new_arc_index])

    return result


def filter_arc(
        arc: ArcData,
        polygon: Polygon,
        dilated_boundaries: list,
        step: float
) -> ArcData | None:
    """
    Return None for any arc that is very close to the edge of the part in
    its entirety, too short to be useful, or does not intersect the polygon.
    """
    if len(arc.path.coords) < 3:
        return None

    if arc.path.length <= step / 20:
        # Arc too short to care about.
        return None

    if not arc.path.intersects(polygon):
        return None

    poly_arc = Polygon(arc.path)
    for ring in dilated_boundaries:
        if ring.contains(poly_arc):
            return None

    return arc
