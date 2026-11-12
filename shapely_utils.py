import math

from typing import List
from typing import Tuple
from typing import Optional
from typing import cast


from shapely import BufferJoinStyle
import shapely.geometry
import shapely.ops
from shapely.validation import make_valid
from shapely.validation import explain_validity

from shapely.geometry import Point
from shapely.geometry import LinearRing
from shapely.geometry import LineString
from shapely.geometry import MultiLineString
from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.geometry import GeometryCollection


class ShapelyUtils:
    """
    Helper functions on Shapely
    """

    @classmethod
    def diff(
        cls,
        paths1: MultiLineString,
        paths2: MultiLineString,
    ) -> MultiLineString:
        """
        Return difference between to MultiLineString geometries. Returns new MultiLineString geometry.
        """
        diffs = []

        for path1, path2 in zip(paths1.geoms, paths2.geoms):
            diff = path1.difference(path2)

            if diff.geom_type == LineString:
                diff = cast(LineString, diff)
                diffs.append(diff)

        return MultiLineString(diffs)

    @classmethod
    def crosses(
        cls,
        bounds: MultiLineString | MultiPolygon,
        p1: Tuple[float, ...],
        p2: Tuple[float, ...],
    ) -> bool:
        """
        Does the line from p1 to p2 cross outside of bounds?
        """
        if bounds == None:
            return True
        if p1[0] == p2[0] and p1[1] == p2[1]:
            return False

        p1_p2 = LineString([p1, p2])

        collection = GeometryCollection([bounds, p1_p2])
        # ShapelyMatplotlib.display(
        #    "mergePath bounds check crosses (multilines) : %d" % cls.cnt,
        #    collection)

        result = p1_p2.intersection(bounds)

        if result.is_empty is True:
            return False

        if result.geom_type == "Point":
            result = cast(Point, result)
            if result.x == p1[0] and result.y == p1[1]:
                return False
            if result.x == p2[0] and result.y == p2[1]:
                return False
        if result.geom_type == "LineString":
            return True
        if result.geom_type == "MultiLineString":
            return True

        return True

    @classmethod
    def simplify_line(
        cls, line: LineString, tol: float
    ) -> MultiLineString:
        """
        Ensure the simplification of a Line is a MultiLine (possibly empty)
        """
        res = line.simplify(tol)

        lines: list[LineString] = []

        if res.geom_type == "LineString":
            res = cast(LineString, res)
            if not res.is_empty:
                lines.append(res)
        if res.geom_type == "MultiLineString":
            res = cast(MultiLineString, res)
            for xline in res.geoms:
                if not xline.is_empty:
                    lines.append(xline)

        return MultiLineString(lines)

    @classmethod
    def simplify_multiline(
        cls, multiline: MultiLineString, tol: float
    ) -> MultiLineString:
        """
        Ensure the simplification of a MultiLine is a Multiline (possibly empty)
        """
        lines: list[LineString] = []
        for line in multiline.geoms:
            xline = line.simplify(tol)
            if xline and xline.geom_type == "LineString":
                xline = cast(LineString, xline)
                lines.append(xline)
            # if xline and xline.geom_type == "MultiLineString":
            #    xline = cast(MultiLineString, xline)
            #    for item in xline.geoms:
            #        lines.append(item)

        return MultiLineString(lines)

    @classmethod
    def simplify_multipoly(
        cls, multipoly: MultiPolygon, tol: float
    ) -> MultiPolygon:
        """
        Ensure the simplification of a MultiPolygon is a MultiPolygon (possibly empty)
        """
        polys: list[Polygon] = []
        for poly in multipoly.geoms:
            geom = poly.simplify(tol)
            if geom and geom.geom_type == "Polygon":
                xpoly = cast(Polygon, geom)
                polys.append(xpoly)
            if geom and geom.geom_type == "MultiPolygon":
                xpolys = cast(MultiPolygon, geom)
                for xpoly in xpolys.geoms:
                    polys.append(xpoly)
            # if geom and geom.geom_type == "GeometryCollection":
            #    geom = cast(GeometryCollection, geom)

        return MultiPolygon(polys)

    @classmethod
    def offset_line(
        cls,
        line: LineString,
        amount: float,
        side: str,
        resolution=16,
        join_style=BufferJoinStyle.round,
        mitre_limit=5.0,
    ) -> LineString | MultiLineString:
        """ """
        return line.parallel_offset(
            amount,
            side,
            resolution=resolution,
            join_style=join_style,
            mitre_limit=mitre_limit,
        )

    @classmethod
    def offset_multiline(
        cls,
        multiline: MultiLineString,
        amount: float,
        side: str,
        resolution=16,
        join_style=BufferJoinStyle.round,
        mitre_limit=5.0,
    ) -> MultiLineString:
        """ """
        offseted_lines = [
            cls.offset_line(line, amount, side, resolution, join_style, mitre_limit)
            for line in multiline.geoms
        ]

        # resulting linestring can be empty
        filtered_lines: list[LineString] = []

        for geom in offseted_lines:
            if geom.geom_type == "LineString":
                if geom.is_empty:
                    continue

                line = cast(LineString, geom)
                filtered_lines.append(line)
            if geom.geom_type == "MultiLineString":
                geom = cast(MultiLineString, geom)
                for line in geom.geoms:
                    if line.is_empty:
                        continue
                    filtered_lines.append(line)

        return MultiLineString(filtered_lines)

    @classmethod
    def orient_multipolygon(
        cls, multipoly: MultiPolygon
    ) -> MultiPolygon:
        """ """
        geoms = []
        for geom in multipoly.geoms:
            xgeom = shapely.geometry.polygon.orient(geom)
            geoms.append(xgeom)

        xmultipoly = MultiPolygon(geoms)

        return xmultipoly

    @classmethod
    def offset_multipolygon(
        cls,
        geometry: MultiPolygon,
        amount: float,
        side,
        consider_interiors_offsets=False,
        resolution=16,
        join_style=BufferJoinStyle.round,
        mitre_limit=5.0,
    ) -> MultiPolygon:
        """
        Generate offseted polygons.
        """
        from shapely_ext import ShapelyMultiPolygonOffset

        offsetser = ShapelyMultiPolygonOffset(geometry)
        return offsetser.offset(
            amount,
            side,
            consider_interiors_offsets,
            resolution,
            join_style,
            mitre_limit,
        )

    @classmethod
    def offset_multipolygon_interiors(
        cls,
        geometry: MultiPolygon,
        amount: float,
        side,
        consider_exteriors_offsets=False,
        resolution=16,
        join_style=BufferJoinStyle.round,
        mitre_limit=5.0,
    ) -> Optional[MultiPolygon]:
        """
        Generate offseted polygons.
        """
        from shapely_ext import ShapelyMultiPolygonOffsetInteriors

        offsetser = ShapelyMultiPolygonOffsetInteriors(geometry)
        return offsetser.offset(
            amount,
            side,
            consider_exteriors_offsets,
            resolution,
            join_style,
            mitre_limit,
        )

    @classmethod
    def build_multipoly_from_offsets(
        cls,
        multi_offset: List[
            LineString | MultiLineString
        ],
    ) -> MultiPolygon:
        """
        offset is the direct result of an parallel_offset operation -> can be of various type

        We filter the degenerated lines

        Warning: shapely offset of a Linestring can produce a MultiLineString.
        This is a problem!

        Example: an interior offset 'right' (-> become bigger) should be a LineString, not
        a MultiineString. As pycut builds from this offset polygons to diff with the offset
        of the exterior, this is a huge problem. See Tudor "AD"
        Hint: simplify the interior first, then maybe the offset is "ok" i.e. is
        a simple LineString

        Todo: considering interiors offseted 'right', pycut could the MultiLineString
        into a single LineString ?
        """
        polygons: list[Polygon] = []

        for offset in multi_offset:
            lines_ok: list[LineString] = []

            if offset.geom_type == "LineString":
                offset = cast(LineString, offset)
                # if not offset.is_empty:
                if len(list(offset.coords)) > 2:
                    lines_ok.append(offset)
            elif offset.geom_type == "MultiLineString":
                offset = cast(MultiLineString, offset)
                for line in offset.geoms:
                    # if not line.is_empty:
                    if len(list(line.coords)) > 2:
                        lines_ok.append(line)

            for line_ok in lines_ok:
                polygon = Polygon(line_ok)

                if polygon.is_valid:
                    polygons.append(polygon)
                else:
                    print("build_multipoly_from_offsets: " + explain_validity(polygon))
                    res = make_valid(polygon)
                    # hoping the result is valid!
                    if res.geom_type == "Polygon":
                        poly = cast(Polygon, res)
                        polygons.append(poly)
                    if res.geom_type == "MultiPolygon":
                        res = cast(MultiPolygon, res)
                        for poly in res.geoms:
                            polygons.append(polygon)
                    if res.geom_type == "GeometryCollection":
                        res = cast(GeometryCollection, res)
                        for geom in res.geoms:
                            if geom.geom_type == "Polygon":
                                geom = cast(Polygon, geom)
                                polygons.append(geom)
                            if geom.geom_type == "MultiPolygon":
                                geom = cast(MultiPolygon, geom)
                                for poly in geom.geoms:
                                    polygons.append(polygon)

        polygons_ok = []
        for poly in polygons:
            if poly.is_valid:
                polygon = shapely.geometry.polygon.orient(poly)
                # tudor 'D' fix - sonce unary_union exception
                polygons_ok.append(polygon)
            else:
                print("build_multipoly_from_offsets: " + explain_validity(polygon))

        multipoly = ShapelyUtils.build_multipoly_from_list_of_polygons(polygons_ok)

        return multipoly

    @classmethod
    def build_multipoly_from_list_of_polygons(
        cls, polygons: List[Polygon]
    ) -> MultiPolygon:
        """ """
        union = shapely.ops.unary_union(polygons)

        if union.geom_type == "Polygon":
            union = cast(Polygon, union)
            multipoly = MultiPolygon([union])
        elif union.geom_type == "MultiPolygon":
            union = cast(MultiPolygon, union)
            multipoly = union
        elif union.geom_type == "GeometryCollection":
            union = cast(GeometryCollection, union)
            polys: list[Polygon] = []
            for item in union.geoms:
                if item.geom_type == "Polygon":
                    item = cast(Polygon, item)
                    polys.append(item)
                elif union.geom_type == "MultiPolygon":
                    item = cast(MultiPolygon, item)
                    polys.extend(list(item.geoms))
            multipoly = MultiPolygon(polys)

        # ensure orientation
        multipoly = ShapelyUtils.orient_multipolygon(multipoly)

        # print("multipoly VALID ?", multipoly.is_valid)

        return multipoly

    @classmethod
    def multipoly_exteriors_to_multiline(
        cls, multipoly: MultiPolygon
    ) -> MultiLineString:
        """ """
        lines = []

        for poly in multipoly.geoms:
            linearring = poly.exterior
            line = ShapelyUtils.linearring_to_linestring(linearring)
            lines.append(line)

        multiline = MultiLineString(lines)

        return multiline

    @classmethod
    def multipoly_interiors_to_multiline(
        cls, multipoly: MultiPolygon
    ) -> MultiLineString:
        """ """
        lines = []

        for poly in multipoly.geoms:
            for interior in poly.interiors:
                line = LineString(interior)
                lines.append(line)

        multiline = MultiLineString(lines)

        return multiline

    @classmethod
    def multiline_to_multipoly(
        cls, multiline: MultiLineString
    ) -> MultiPolygon:
        """result may be empty"""
        polys = []

        for line in multiline.geoms:
            poly = Polygon(line)
            polys.append(poly)

        multipoly = MultiPolygon(polys)

        valid = make_valid(multipoly)

        if valid.geom_type == "Polygon":
            valid = cast(Polygon, valid)
            return MultiPolygon([valid])
        if valid.geom_type == "MultiPolygon":
            valid = cast(MultiPolygon, valid)
            return valid
        if valid.geom_type == "GeometryCollection":
            valid = cast(GeometryCollection, valid)
            for item in valid.geoms:
                if item.geom_type == "Polygon":
                    item = cast(Polygon, item)
                    return MultiPolygon([item])
                if item.geom_type == "MultiPolygon":
                    item = cast(MultiPolygon, item)
                    return item

        return MultiPolygon([])  # empty

    @classmethod
    def remove_multipoly_holes(
        cls, multipoly: MultiPolygon
    ) -> MultiPolygon:
        epolys = []

        for poly in multipoly.geoms:
            line = LineString(poly.exterior)
            epoly = Polygon(line)

            epolys.append(epoly)

        return MultiPolygon(epolys)

    @classmethod
    def reorder_poly_points(
        cls, polygon: Polygon
    ) -> Polygon:
        """
        Problem: shapely bug when outsetting a polygon where the starting point
        is a convex corner: at that point, the offset line 'outside' is uncorrect.

        Solution: start the list of points at a point in the middle of a segment
        (if there is one)
        """
        if not polygon.geom_type == "Polygon":
            return polygon

        # -----------------------------------------------------
        def make_no_edges(pts):
            pt1 = pts[0]
            pt2 = pts[1]

            mx = (pt1[0] + pt2[0]) / 2.0
            my = (pt1[1] + pt2[1]) / 2.0

            middle_pt0_pt1 = (mx, my)

            return [middle_pt0_pt1] + pts[1:] + [pts[0]]

        # -----------------------------------------------------

        pts_e = list(polygon.exterior.coords)
        pts = make_no_edges(pts_e)

        holes = []

        for interiors in polygon.interiors:
            pts_i = list(interiors.coords)
            pts_ii = make_no_edges(pts_i)

            holes.append(LineString(pts_ii))

        return Polygon(pts, holes=holes)

    @classmethod
    def fix_multipoly(
        cls, multipoly: MultiPolygon
    ) -> MultiPolygon:
        """ """
        valid_polys = []

        for poly in multipoly.geoms:
            if not poly.is_valid:
                fixed_poly = cls.fix_generic_polygon(poly)
                valid_polys.append(fixed_poly)
            else:
                valid_polys.append(poly)

        return MultiPolygon(valid_polys)

    @classmethod
    def fix_simple_polygon(
        cls, polygon: Polygon
    ) -> Polygon:
        """ """
        valid = make_valid(polygon)

        if valid.geom_type == "Polygon":
            poly = cast(Polygon, valid)
            return poly

        elif valid.geom_type == "MultiPolygon":
            multipoly = cast(MultiPolygon, valid)
            return cls.select_largest_poly_from_multipoly(multipoly)

        elif valid.geom_type == "GeometryCollection":
            collection = cast(GeometryCollection, valid)
            return cls.select_largest_poly_from_collection(collection)

        return Polygon([])

    @classmethod
    def select_largest_poly_from_multipoly(
        cls, multipoly: MultiPolygon
    ) -> Polygon:
        """ """
        largest_area = 0.0
        largest_poly = Polygon([])

        for poly in multipoly.geoms:
            area = poly.area
            if area > largest_area:
                largest_area = area
                largest_poly = poly

        return largest_poly

    @classmethod
    def select_largest_poly_from_collection(
        cls, collection: GeometryCollection
    ) -> Polygon:
        """ """
        largest_area = 0.0
        largest_poly = Polygon([])

        for geom in collection.geoms:
            if geom.geom_type == "MultiPolygon":
                multipoly = cast(MultiPolygon, geom)
                l_poly = cls.select_largest_poly_from_multipoly(multipoly)

                if l_poly.area > largest_area:
                    largest_area = l_poly.area
                    largest_poly = l_poly

            elif geom.geom_type == "Polygon":
                poly = cast(Polygon, geom)
                area = poly.area
                if area > largest_area:
                    largest_area = area
                    largest_poly = poly

            elif geom.geom_type == "MultiLineString":
                pass
            elif geom.geom_type == "LineString":
                pass

        return largest_poly

    @classmethod
    def fix_generic_polygon(
        cls, polygon: Polygon
    ) -> Polygon:
        """
        fix exterior and interiors if not valid
        """
        if polygon.is_valid:
            return polygon

        exterior = polygon.exterior
        interiors = polygon.interiors

        ext_poly = Polygon(exterior)
        if not ext_poly.is_valid:
            ext_poly = cls.fix_simple_polygon(ext_poly)

        if not interiors:
            ext_linestring = LineString(ext_poly.exterior)

            fixed_poly = Polygon(ext_linestring)
        else:
            fixed_interiors: List[Polygon] = []
            for interior in interiors:
                int_poly = Polygon(interior)

                if not int_poly.is_valid:
                    int_poly = cls.fix_simple_polygon(int_poly)

                fixed_interiors.append(int_poly)

            ext_linestring = LineString(ext_poly.exterior)
            holes_linestrings = [
                LineString(int_poly.exterior)
                for int_poly in fixed_interiors
            ]

            fixed_poly = Polygon(
                ext_linestring, holes=holes_linestrings
            )

        return fixed_poly

    @classmethod
    def linearring_to_linestring(
        cls, linearring: LinearRing
    ) -> LineString:
        """
        remove duplicated last point and returns as linestring
        """
        xs = linearring.coords.xy[0]
        ys = linearring.coords.xy[1]

        first = (xs[0], ys[0])
        last = (xs[-1], ys[-1])

        dd = ShapelyUtils.dist(first, last)

        if dd < 1.0e-8:
            coordinates = list(zip(xs[:-1], ys[:-1]))

            return LineString(coordinates)

        return LineString(linearring)

    @classmethod
    def dist(cls, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        return dx * dx + dy * dy
