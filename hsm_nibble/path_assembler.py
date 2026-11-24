"""
PathAssembler: converts a stream of ArcData segments into a final ordered
toolpath, inserting connecting moves between arcs.

Also contains split_line_by_poly, a geometry utility used only here.
"""

from shapely.geometry import LineString, MultiLineString, MultiPolygon, Point, Polygon  # type: ignore
from shapely.ops import split  # type: ignore
from shapely.errors import GeometryTypeError

from hsm_nibble.arc_utils import (
    ArcData, ArcDir, LineData, MoveStyle,
    complete_arc,
)

# Trivially short lines joining arcs should be filtered.
SHORTEST_RAPID = 1e-6


def split_line_by_poly(line: LineString, poly: Polygon | MultiPolygon) -> MultiLineString:
    """
    split() sometimes fails if line shares a point with one of poly's rings.
    Splits line against every ring of poly individually to work around that.
    """
    if isinstance(poly, Polygon):
        poly = MultiPolygon([poly])
    rings = []
    for p in poly.geoms:
        if not isinstance(p, Polygon):
            continue
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
                checked_lines.append(LineString([last_new_line.coords[-1], new_line.coords[0]]))
        checked_lines.append(new_line)
        last_new_line = new_line
    assert last_new_line is not None
    if last_new_line.coords[-1] != line.coords[-1]:
        checked_lines.append(LineString([last_new_line.coords[-1], line.coords[-1]]))

    return MultiLineString(checked_lines)


class PathAssembler:
    """
    Converts a stream of ArcData segments into a final ordered toolpath.

    Responsibilities:
    - Maintain the output path list (ArcData and LineData moves).
    - Insert connecting moves (cut, rapid-inside, or rapid-outside) between arcs.
    - Buffer incoming arcs in per-branch queues so that split arcs (caused by
      already-cut areas) are interleaved correctly.
    - Track cut_area_total — the area swept by arcs that have actually been
      appended to the path (distinct from Pocket.calculated_area_total, which
      tracks arcs that have been planned but not yet output).
    """

    def __init__(
            self,
            step: float,
            winding_dir: ArcDir,
            cut_area_total: Polygon,
            dilated_starting_polygon: Polygon,
    ) -> None:
        self.step = step
        self.winding_dir = winding_dir
        self.cut_area_total: Polygon = cut_area_total
        self.dilated_starting_polygon = dilated_starting_polygon
        self.path: list[ArcData | LineData] = []
        self.pending_arc_queues: list[list[ArcData]] = []
        self.last_arc: ArcData | None = None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def queue_arcs(self, new_arcs: list[ArcData]) -> None:
        """
        Buffer new_arcs into the appropriate per-branch queue and drain any
        queue that is safe to process immediately.

        When an arc intersects an already-cut area it is split into several
        pieces, each of which belongs to a different branch of the path.
        Arcs in the same branch should be connected to each other; arcs in
        different branches get separate connecting moves.  queue_arcs assigns
        each arc to the closest existing queue (or opens a new one) and
        flushes a queue whenever it can safely do so.
        """
        modified_queues_indexes = set()

        if len(new_arcs) == 1 and len(self.pending_arc_queues) == 1:
            # Fast path: single queue, single arc — no need for distance math.
            self.pending_arc_queues[0].append(new_arcs[0])
            to_process = self.pending_arc_queues.pop(0)
            self._arcs_to_path(to_process)
            return

        closest_queue: list[ArcData] | None
        for arc in new_arcs:
            closest_queue = None
            closest_queue_index = None
            closest_dist = self.step
            for queue_index, queue in enumerate(self.pending_arc_queues):
                if self.winding_dir == ArcDir.CLOSEST:
                    combined_dist = 1
                    seperate_dist = 0
                else:
                    assert arc.start is not None
                    assert queue[-1].start is not None
                    assert queue[-1].end is not None

                    seperate_dist = (
                            queue[-1].start.distance(queue[-1].end) + arc.start.distance(arc.end))
                    combined_dist = (
                            queue[-1].start.distance(arc.end) + queue[-1].end.distance(arc.start))

                seperation = arc.path.distance(queue[-1].path)
                if seperation < closest_dist or combined_dist < seperate_dist:
                    if self._check_queue_overlap(arc, queue_index):
                        closest_dist = seperation
                        closest_queue = queue
                        closest_queue_index = queue_index
            if closest_queue is None:
                closest_queue = []
                closest_queue_index = len(self.pending_arc_queues)
                self.pending_arc_queues.append(closest_queue)
            closest_queue.append(arc)
            modified_queues_indexes.add(closest_queue_index)
            assert closest_queue_index is not None
            assert closest_queue is self.pending_arc_queues[closest_queue_index]
            assert arc in closest_queue

        if modified_queues_indexes and 0 not in modified_queues_indexes:
            to_process = self.pending_arc_queues.pop(0)
            self._arcs_to_path(to_process)

    def flush_arc_queues(self) -> None:
        """Drain all remaining queues, in FIFO order."""
        while self.pending_arc_queues:
            to_process = self.pending_arc_queues.pop(0)
            self._arcs_to_path(to_process)

    def join_arcs(self, next_arc: ArcData) -> list[LineData]:
        """
        Generate the connecting move from the end of the last arc to the start
        of next_arc. Also updates cut_area_total to include next_arc's swept area.

        Returns a list of LineData moves (may be empty if the arcs are adjacent).
        """
        assert self.last_arc

        arc_poly = Polygon(list(next_arc.path.coords) + [next_arc.origin]).buffer(self.step / 20)
        to_cut_area_total = self.cut_area_total.union(arc_poly)

        lines = []
        path = LineString([self.last_arc.end, next_arc.start])
        inside_pocket = (
                path.covered_by(self.dilated_starting_polygon)
                or path.covered_by(to_cut_area_total)
                )

        if inside_pocket:
            if path.length <= self.step:
                return [LineData(
                        Point(path.coords[0]),
                        Point(path.coords[-1]),
                        path,
                        MoveStyle.CUT,
                        )]

            split_for_last = path.interpolate(-self.step)
            last_line = LineData(
                    Point(split_for_last),
                    Point(next_arc.start),
                    LineString([split_for_last, next_arc.start]),
                    MoveStyle.CUT,
                    )

            remaining_path = LineString([self.last_arc.end, split_for_last])

            sweep = remaining_path.buffer(self.step / 2)
            crash = sweep.difference(self.cut_area_total)
            if crash.area / sweep.area <= 0.05:
                move_style = MoveStyle.RAPID_INSIDE
            else:
                move_style = MoveStyle.CUT

            line = LineData(
                    Point(remaining_path.coords[0]),
                    Point(remaining_path.coords[-1]),
                    remaining_path,
                    move_style,)

            if line.path.length > SHORTEST_RAPID:
                lines.append(line)
            lines.append(last_line)
        else:
            move_style = MoveStyle.RAPID_OUTSIDE
            line = LineData(self.last_arc.end, next_arc.start, path, move_style,)
            if line.path.length > SHORTEST_RAPID:
                lines.append(line)

        self.cut_area_total = to_cut_area_total

        return lines

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _check_queue_overlap(self, arc: ArcData, queue_index: int) -> bool:
        """
        Return True when arc can safely be appended to the queue at queue_index
        (i.e. no later queue contains an arc whose swept area overlaps arc).
        """
        dilated_arc = arc.path.buffer(self.step)
        for queue in self.pending_arc_queues[queue_index + 1:]:
            for existing_arc in queue:
                if existing_arc.path.intersects(dilated_arc):
                    return False
        return True

    def _arcs_to_path(self, arcs: list[ArcData]) -> None:
        """
        Pop arcs from the list, insert connecting moves, and append to self.path.
        Modifies arcs in place.
        """
        while arcs:
            arc = arcs.pop(0)
            if arc is None:
                continue

            winding_dir = self.winding_dir
            last_arc = self.last_arc
            if winding_dir == ArcDir.CLOSEST:
                if last_arc is None:
                    winding_dir = ArcDir.CW
                else:
                    if last_arc.winding_dir == ArcDir.CCW:
                        winding_dir = ArcDir.CW
                    else:
                        winding_dir = ArcDir.CCW

                    assert last_arc.start is not None
                    assert last_arc.end is not None

                    end_to_end = last_arc.end.distance(arc.end)
                    if last_arc.end.distance(arc.start) < end_to_end:
                        winding_dir = ArcDir.CW
                    if last_arc.start.distance(arc.end) < end_to_end:
                        winding_dir = ArcDir.CW

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
