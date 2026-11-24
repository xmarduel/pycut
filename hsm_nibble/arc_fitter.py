"""
Arc fitting logic: bisection-based convergence function.

These are extracted from Pocket._calculate_arc so the core algorithm can be
tested in isolation without constructing a full Pocket instance.
"""

#from typing import Callable
from collections.abc import Callable

from shapely.geometry import LineString, Point, Polygon  # type: ignore

from hsm_nibble.arc_utils import (
    ArcData, ArcDir,
    create_circle, split_arcs,
)

# Kept for API compatibility with existing tests and callers.
# The bisection algorithm does not use it but accepts it as an ignored parameter.
ITERATION_COUNT = 50

# When arc sizes drop below a certain point, reduce the step size so the
# distance between arcs doesn't exceed the arc diameter.
# Minimum arc radius as a multiple of overlap at which step reduction begins.
CORNER_ZOOM = 2.0
# How much effect the feature has. 1 = step proportional to arc size.
CORNER_ZOOM_EFFECT = 1.0

# Bisection converges to desired_step / CONVERGE_FRACTION accuracy.
# 30 iterations on a 10-unit bracket gives ~1e-8 precision.
_BISECT_ITERATIONS = 30
_CONVERGE_FRACTION = 20  # stop when |spacing - desired| < desired / 20


class ProportionalController:
    """Kept for API compatibility. Not used by find_best_arc_distance."""

    def __init__(self, kp: float = 0.76) -> None:
        self._kp = kp

    def step(self, target: float, current: float) -> float:
        error = target - current
        return self._kp * error


def extrapolate_line(overshoot: float, line: LineString) -> LineString:
    """
    Extend a line at both ends in the same direction it points.
    Used to give the convergence loop room to overshoot without hitting the
    endpoint clamp of LineString.interpolate().
    """
    coord_0, coord_1 = line.coords[:2]
    coord_m2, coord_m1 = line.coords[-2:]
    ratio_begin = overshoot / LineString([coord_0, coord_1]).length
    ratio_end = overshoot / LineString([coord_m2, coord_m1]).length
    coord_begin = Point(
        coord_0[0] + (coord_0[0] - coord_1[0]) * ratio_begin,
        coord_0[1] + (coord_0[1] - coord_1[1]) * ratio_begin)
    coord_end = Point(
        coord_m1[0] + (coord_m1[0] - coord_m2[0]) * ratio_end,
        coord_m1[1] + (coord_m1[1] - coord_m2[1]) * ratio_end)
    return LineString([coord_begin] + list(line.coords) + [coord_end])


def arc_at_distance(
        distance: float,
        voronoi_edge: LineString,
        distance_from_geom: Callable[[Point], float],
        overshoot: float = 100000,
) -> tuple[Point, float]:
    """
    Calculate the center point and radius of the largest arc that fits at a
    given distance along a voronoi edge.

    The voronoi edge is extrapolated by `overshoot` at each end so that
    callers can pass a raw distance without worrying about endpoint clamping.
    """
    edge_extended = extrapolate_line(overshoot, voronoi_edge)
    pos = edge_extended.interpolate(distance + overshoot)
    radius = distance_from_geom(pos)
    return (pos, radius)


def _desired_step(radius: float, step: float) -> float:
    """Return the corner-zoom-adjusted desired step for an arc of the given radius."""
    threshold = CORNER_ZOOM * step
    if radius < threshold:
        multiplier = (threshold - radius) / threshold
        return step * (1 - CORNER_ZOOM_EFFECT * multiplier)
    return step


def _area_spacing(
        d: float,
        voronoi_edge: LineString,
        winding_dir: ArcDir,
        calculated_area: Polygon,
        distance_from_geom: Callable[[Point], float],
) -> tuple[float | None, ArcData]:
    """
    Return (spacing, circle) where spacing is the maximum distance from any
    visible arc point to the already-cut area boundary, or None if the arc is
    entirely hidden.

    Used at the start of a new Voronoi branch (last_circle is None) to place
    the first arc step away from the nearest already-cut boundary.
    """
    pos, radius = arc_at_distance(d, voronoi_edge, distance_from_geom)
    circle = create_circle(pos, radius, winding_dir)
    arcs = split_arcs([circle], calculated_area)
    if not arcs:
        return None, circle
    spacing = max(
        calculated_area.distance(Point(c))
        for arc in arcs
        for c in arc.path.coords
    )
    return spacing, circle


def _hausdorff_spacing(
        d: float,
        voronoi_edge: LineString,
        winding_dir: ArcDir,
        calculated_area: Polygon,
        last_circle: ArcData,
        distance_from_geom: Callable[[Point], float],
        max_dist: float,
) -> tuple[float | None, ArcData]:
    """
    Return (spacing, circle) where spacing is the Hausdorff-based step from
    last_circle to the visible arcs at distance d, or None if the arc is
    entirely hidden.
    """
    pos, radius = arc_at_distance(d, voronoi_edge, distance_from_geom)
    circle = create_circle(pos, radius, winding_dir)
    arcs = split_arcs([circle], calculated_area)
    if not arcs:
        return None, circle
    spacing = -max_dist
    for arc in arcs:
        spacing = max(
            spacing,
            last_circle.origin.hausdorff_distance(arc.path) - (last_circle.radius or 0))
    return abs(spacing), circle


def find_best_arc_distance(
        voronoi_edge: LineString,
        start_distance: float,
        min_distance: float,
        step: float,
        winding_dir: ArcDir,
        calculated_area: Polygon,
        last_circle: ArcData | None,
        distance_from_geom: Callable[[Point], float],
        max_dist: float,
        controller: ProportionalController | None = None,
) -> tuple[float, ArcData, bool, int, bool]:
    """
    Find the distance along voronoi_edge at which an arc of the correct step
    size fits, using bisection on the Hausdorff spacing between arcs.

    Args:
        voronoi_edge: The line of midpoints between pocket edges.
        start_distance: Distance along voronoi_edge to start searching from.
        min_distance: Unused; kept for API compatibility.
        step: Desired distance between arc passes.
        winding_dir: CW or CCW winding direction for created circles.
        calculated_area: Area already planned — used to clip proposed arcs.
        last_circle: Reference circle for measuring step progress. None at the
            start of a new voronoi branch.
        distance_from_geom: Callable returning distance from a Point to the
            nearest pocket edge.
        max_dist: Maximum voronoi distance; used as a sentinel in spacing calc.
        controller: Ignored. Kept for API compatibility.

    Returns:
        (best_distance, best_circle, hidden_at_start, iteration_count, backwards)

        best_distance: Distance along voronoi_edge of the best-fit arc.
        best_circle: Full circle at best_distance (caller updates last_circle
            and calculated_area_total).
        hidden_at_start: True when the arc at the chosen position is entirely
            inside calculated_area. Caller should record best_circle as
            last_circle and return empty arcs without advancing.
        iteration_count: Number of bisection iterations used.
        backwards: Always False (bisection cannot move backward).

    Spacing metric (why not circle centres):
        Each proposed arc is clipped to its visible portion — the part that
        extends into uncut material — because other Voronoi branches may have
        already cleared part of the full circle. A foreign branch can clear any
        portion of the arc regardless of where its centre lies relative to ours.

        A centre-to-centre distance formula implicitly assumes both arcs are
        full circles and measures to their theoretical far edges. This is wrong:
        it returns "correct" spacing even when the actual visible cutting is a
        small sliver nowhere near the far edge.

        Hausdorff distance from last_circle's centre to the visible arc segment
        measures how far the farthest visible arc point extends past
        last_circle's edge — i.e., how far the tool actually cuts beyond the
        previous pass. This correctly accounts for arbitrary foreign-branch
        clipping.
    """
    # ------------------------------------------------------------------
    # Case 1: start of a new voronoi branch.
    #
    # Bisect using _area_spacing so the first arc is placed step away from
    # the nearest already-cut boundary.  When calculated_area is empty (very
    # start of planning) place at edge start immediately.
    # ------------------------------------------------------------------
    if last_circle is None:
        if calculated_area.is_empty:
            pos, radius = arc_at_distance(start_distance, voronoi_edge, distance_from_geom)
            circle = create_circle(pos, radius, winding_dir)
            return (start_distance, circle, False, 1, False)

        # Scan forward to find the first position where the arc is visible.
        lo = None
        for _n in range(_BISECT_ITERATIONS + 2):
            d = min(start_distance + _n * step, voronoi_edge.length)
            sp, _ = _area_spacing(d, voronoi_edge, winding_dir, calculated_area,
                                  distance_from_geom)
            if sp is not None:
                lo = d
                break
            if d >= voronoi_edge.length:
                break

        if lo is None:
            # Entire edge hidden — advance by one step as a reference circle.
            ref_d = min(start_distance + step, voronoi_edge.length)
            pos, radius = arc_at_distance(ref_d, voronoi_edge, distance_from_geom)
            circle = create_circle(pos, radius, winding_dir)
            return (ref_d, circle, True, 1, False)

        sp_lo, circle_lo = _area_spacing(lo, voronoi_edge, winding_dir, calculated_area,
                                         distance_from_geom)
        if sp_lo is not None and sp_lo >= step:
            # Already at or beyond the target — place here.
            return (lo, circle_lo, False, 1, False)

        # Scan further to find hi where area spacing >= step.
        hi = None
        for _n in range(1, _BISECT_ITERATIONS + 2):
            d = min(lo + _n * step, voronoi_edge.length)
            sp, _ = _area_spacing(d, voronoi_edge, winding_dir, calculated_area,
                                  distance_from_geom)
            if sp is not None and sp >= step:
                hi = d
                break
            if d >= voronoi_edge.length:
                break

        if hi is None:
            pos, radius = arc_at_distance(voronoi_edge.length, voronoi_edge, distance_from_geom)
            circle = create_circle(pos, radius, winding_dir)
            hidden = not split_arcs([circle], calculated_area)
            return (voronoi_edge.length, circle, hidden, 1, False)

        # Bisect between lo (sp < step) and hi (sp >= step).
        best_circle = None
        best_distance = hi
        best_err = float('inf')
        count = 0
        for count in range(1, _BISECT_ITERATIONS + 1):
            mid = (lo + hi) / 2
            sp_mid, circle = _area_spacing(mid, voronoi_edge, winding_dir, calculated_area,
                                           distance_from_geom)
            if sp_mid is None:
                lo = mid
                continue
            err = abs(sp_mid - step)
            if err < best_err:
                best_err = err
                best_circle = circle
                best_distance = mid
            if sp_mid < step:
                lo = mid
            else:
                hi = mid
            if err < step / _CONVERGE_FRACTION:
                break

        if best_circle is None:
            ref_d = min(start_distance + step, voronoi_edge.length)
            pos, radius = arc_at_distance(ref_d, voronoi_edge, distance_from_geom)
            circle = create_circle(pos, radius, winding_dir)
            return (ref_d, circle, True, count, False)

        best_distance = min(best_distance, voronoi_edge.length)
        hidden = not split_arcs([best_circle], calculated_area)
        return (best_distance, best_circle, hidden, count, False)

    # ------------------------------------------------------------------
    # Case 2: near end of edge — place at edge end.
    # ------------------------------------------------------------------
    remaining = voronoi_edge.length - start_distance
    if remaining <= step:
        pos, radius = arc_at_distance(voronoi_edge.length, voronoi_edge, distance_from_geom)
        circle = create_circle(pos, radius, winding_dir)
        hidden = not split_arcs([circle], calculated_area)
        return (voronoi_edge.length, circle, hidden, 1, False)

    # ------------------------------------------------------------------
    # Case 3: bisect to find the distance where Hausdorff spacing = desired.
    #
    # lo=start_distance is always inside calculated_area (it's where the
    # previous arc was placed), so spacing there is 0 — no need to evaluate.
    #
    # hi is found by scanning forward in step increments until we reach a
    # position where the arc is visible AND spacing >= desired. Expanding
    # directly to edge_end risks non-monotone behaviour on long curved edges,
    # where bisection would find a spurious far solution.
    # ------------------------------------------------------------------
    lo = start_distance
    hi = None
    for _n in range(2, _BISECT_ITERATIONS + 2):
        hi_candidate = min(start_distance + _n * step, voronoi_edge.length)
        sp_candidate, _ = _hausdorff_spacing(
            hi_candidate, voronoi_edge, winding_dir, calculated_area, last_circle,
            distance_from_geom, max_dist)
        _, r_candidate = arc_at_distance(hi_candidate, voronoi_edge, distance_from_geom)
        if sp_candidate is not None and sp_candidate >= _desired_step(r_candidate, step):
            hi = hi_candidate
            break
        if hi_candidate >= voronoi_edge.length:
            break

    # If no valid hi found, place at edge end and return.
    if hi is None:
        pos, radius = arc_at_distance(voronoi_edge.length, voronoi_edge, distance_from_geom)
        circle = create_circle(pos, radius, winding_dir)
        hidden = not split_arcs([circle], calculated_area)
        return (voronoi_edge.length, circle, hidden, 1, False)

    # Bisect. Hidden arcs (sp_mid is None) are treated as spacing=0 → push lo up.
    # Track the closest match by |spacing - desired| regardless of direction —
    # this handles convergence from below (sp just under desired) where the
    # hi boundary is never updated and best_circle would otherwise be None.
    best_circle = None
    best_distance = hi
    best_err = float('inf')
    count = 0
    for count in range(1, _BISECT_ITERATIONS + 1):
        mid = (lo + hi) / 2
        sp_mid, circle = _hausdorff_spacing(
            mid, voronoi_edge, winding_dir, calculated_area, last_circle,
            distance_from_geom, max_dist)

        if sp_mid is None:
            lo = mid
            continue

        _, mid_radius = arc_at_distance(mid, voronoi_edge, distance_from_geom)
        desired = _desired_step(mid_radius, step)
        err = abs(sp_mid - desired)

        if err < best_err:
            best_err = err
            best_circle = circle
            best_distance = mid

        if sp_mid < desired:
            lo = mid
        else:
            hi = mid

        if err < desired / _CONVERGE_FRACTION:
            break

    if best_circle is None:
        # All positions in [lo, hi] were hidden — advance by one step as a
        # reference circle so the next call measures from start_distance+step.
        ref_d = min(start_distance + step, voronoi_edge.length)
        pos, radius = arc_at_distance(ref_d, voronoi_edge, distance_from_geom)
        ref_circle = create_circle(pos, radius, winding_dir)
        return (ref_d, ref_circle, True, count, False)

    best_distance = min(best_distance, voronoi_edge.length)
    hidden = not split_arcs([best_circle], calculated_area)
    return (best_distance, best_circle, hidden, count, False)
