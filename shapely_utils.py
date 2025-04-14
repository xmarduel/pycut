import math

from typing import List
from typing import Tuple

import shapely.geometry  # type: ignore [import-untyped]
import shapely.ops  # type: ignore [import-untyped]
from shapely.validation import make_valid  # type: ignore [import-untyped]
from shapely.validation import explain_validity  # type: ignore [import-untyped]

from shapely_matplotlib import MatplotLibUtils  # type: ignore [import-untyped]


class ShapelyUtils:
    """
    Helper functions on Shapely
    """

    MAPLOTLIB_DEBUG = False
    # MAPLOTLIB_DEBUG = True
    cnt = 1  # matplotlin figures

    @classmethod
    def diff(
        cls,
        paths1: shapely.geometry.MultiLineString,
        paths2: shapely.geometry.MultiLineString,
    ) -> shapely.geometry.MultiLineString:
        """
        Return difference between to MultiLineString geometries. Returns new MultiLineString geometry.
        """
        diffs = [
            path1.difference(path2)
            for (path1, path2) in zip(paths1.geoms, paths2.geoms)
        ]

        return shapely.geometry.MultiLineString(diffs)

    @classmethod
    def crosses(
        cls,
        bounds: shapely.geometry.MultiPolygon,
        p1: Tuple[int, int],
        p2: Tuple[int, int],
    ) -> bool:
        """
        Does the line from p1 to p2 cross outside of bounds?
        """
        if bounds == None:
            return True
        if p1[0] == p2[0] and p1[1] == p2[1]:
            return False

        p1_p2 = shapely.geometry.LineString([p1, p2])

        collection = shapely.geometry.GeometryCollection([bounds, p1_p2])
        # MatplotLibUtils.display(
        #    "mergePath bounds check crosses (multilines) : %d" % cls.cnt,
        #    collection)

        result = p1_p2.intersection(bounds)

        if result.is_empty is True:
            return False

        if result.geom_type == "Point":
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
    def simplify_multiline(
        cls, multiline: shapely.geometry.MultiLineString, tol: float
    ) -> shapely.geometry.MultiLineString | None:
        """
        Ensure the simplification of a MultiLine is a Multiline or None
        """
        lines = []
        for line in multiline.geoms:
            xline = line.simplify(tol)
            if xline and xline.geom_type == "LineString":
                lines.append(xline)

        if lines:
            res = shapely.geometry.MultiLineString(lines)
        else:
            res = None

        return res

    @classmethod
    def simplify_multipoly(
        cls, multipoly: shapely.geometry.MultiPolygon, tol: float
    ) -> shapely.geometry.MultiPolygon | None:
        """
        Ensure the simplification of a MultiPolygon is a MultiPolygon or None
        """
        polys = []
        for poly in multipoly.geoms:
            xpoly = poly.simplify(tol)
            if xpoly and xpoly.geom_type == "Polygon":
                polys.append(xpoly)

        if polys:
            res = shapely.geometry.MultiPolygon(polys)
        else:
            res = None

        return res

    @classmethod
    def offset_line(
        cls,
        line: shapely.geometry.LineString,
        amount: float,
        side: str,
        resolution=16,
        join_style=1,
        mitre_limit=5.0,
    ) -> shapely.geometry.LineString | shapely.geometry.MultiLineString:
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
        multiline: shapely.geometry.MultiLineString,
        amount: float,
        side: str,
        resolution=16,
        join_style=1,
        mitre_limit=5.0,
    ) -> shapely.geometry.MultiLineString:
        """ """
        offseted_lines = [
            cls.offset_line(line, amount, side, resolution, join_style, mitre_limit)
            for line in multiline.geoms
        ]

        # resulting linestring can be empty
        filtered_lines = []

        for geom in offseted_lines:
            if geom.geom_type == "LineString":
                if geom.is_empty:
                    continue
                filtered_lines.append(geom)
            if geom.geom_type == "MultiLineString":
                for line in geom.geoms:
                    if line.is_empty:
                        continue
                    filtered_lines.append(line)

        if len(filtered_lines) == 0:
            return None

        offsetted = shapely.geometry.MultiLineString(filtered_lines)

        return offsetted

    @classmethod
    def orient_multipolygon(
        cls, multipoly: shapely.geometry.MultiPolygon
    ) -> shapely.geometry.MultiPolygon:
        """ """
        geoms = []
        for geom in multipoly.geoms:
            xgeom = shapely.geometry.polygon.orient(geom)
            geoms.append(xgeom)

        xmultipoly = shapely.geometry.MultiPolygon(geoms)

        return xmultipoly

    @classmethod
    def offset_multipolygon(
        cls,
        geometry: shapely.geometry.MultiPolygon,
        amount: float,
        side,
        consider_interiors_offsets=False,
        resolution=16,
        join_style=1,
        mitre_limit=5.0,
    ) -> shapely.geometry.MultiPolygon:
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
        geometry: shapely.geometry.MultiPolygon,
        amount: float,
        side,
        consider_exteriors_offsets=False,
        resolution=16,
        join_style=1,
        mitre_limit=5.0,
    ) -> shapely.geometry.MultiPolygon | None:
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
            shapely.geometry.LineString | shapely.geometry.MultiLineString
        ],
    ) -> shapely.geometry.MultiPolygon:
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
        polygons = []

        for offset in multi_offset:
            lines_ok = []
            if offset.geom_type == "LineString":
                if len(list(offset.coords)) <= 2:
                    pass
                else:
                    lines_ok.append(offset)
            elif offset.geom_type == "MultiLineString":
                for geom in offset.geoms:
                    if geom.geom_type == "LineString":
                        if len(list(geom.coords)) <= 2:
                            continue
                        lines_ok.append(geom)

            for line_ok in lines_ok:
                polygon = shapely.geometry.Polygon(line_ok)

                if polygon.is_valid:
                    polygons.append(polygon)
                else:
                    print("build_multipoly_from_offsets: " + explain_validity(polygon))
                    res = make_valid(polygon)
                    # hoping the result is valid!
                    if res.geom_type == "Polygon":
                        polygons.append(polygon)
                    if res.geom_type == "MultiPolygon":
                        for poly in res.geoms:
                            polygons.append(polygon)
                    if res.geom_type == "GeometryCollection":
                        for geom in res.geoms:
                            if geom.geom_type == "Polygon":
                                polygons.append(polygon)
                            if geom.geom_type == "MultiPolygon":
                                for poly in geom.geoms:
                                    polygons.append(polygon)

        polygons_ok = []
        for poly in polygons:
            polygon = shapely.geometry.polygon.orient(poly)
            if polygon.is_valid:
                # tudor 'D' fix - sonce unary_union exception
                polygons_ok.append(polygon)
            else:
                print("build_multipoly_from_offsets: " + explain_validity(polygon))

        multipoly = ShapelyUtils.build_multipoly_from_list_of_polygons(polygons_ok)

        return multipoly

    @classmethod
    def build_multipoly_from_list_of_polygons(
        cls, polygons: List[shapely.geometry.Polygon]
    ) -> shapely.geometry.MultiPolygon:
        """ """
        union = shapely.ops.unary_union(polygons)

        if union.geom_type == "Polygon":
            multipoly = shapely.geometry.MultiPolygon([union])
        elif union.geom_type == "MultiPolygon":
            multipoly = union
        elif union.geom_type == "GeometryCollection":
            polygons = []
            for item in union.geoms:
                if item.geom_type == "Polygon":
                    polygons.append(item)
                elif union.geom_type == "MultiPolygon":
                    polygons.extend(list(union.geoms))
            multipoly = shapely.geometry.MultiPolygon(polygons)

        # ensure orientation
        multipoly = ShapelyUtils.orient_multipolygon(multipoly)

        # print("multipoly VALID ?", multipoly.is_valid)

        return multipoly

    @classmethod
    def multipoly_exteriors_to_multiline(
        cls, multipoly: shapely.geometry.MultiPolygon
    ) -> shapely.geometry.MultiLineString:
        """ """
        lines = []

        for poly in multipoly.geoms:
            linearring = poly.exterior
            line = ShapelyUtils.linearring_to_linestring(linearring)
            lines.append(line)

        multiline = shapely.geometry.MultiLineString(lines)

        return multiline

    @classmethod
    def multipoly_interiors_to_multiline(
        cls, multipoly: shapely.geometry.MultiPolygon
    ) -> shapely.geometry.MultiLineString:
        """ """
        lines = []

        for poly in multipoly.geoms:
            for interior in poly.interiors:
                line = shapely.geometry.LineString(interior)
                lines.append(line)

        multiline = shapely.geometry.MultiLineString(lines)

        return multiline

    @classmethod
    def multiline_to_multipoly(
        cls, multiline: shapely.geometry.MultiLineString
    ) -> shapely.geometry.MultiPolygon:
        """ """
        polys = []

        for line in multiline.geoms:
            poly = shapely.geometry.Polygon(line)
            polys.append(poly)

        multipoly = shapely.geometry.MultiPolygon(polys)
        multipoly = make_valid(multipoly)

        return multipoly

    @classmethod
    def remove_multipoly_holes(
        cls, multipoly: shapely.geometry.MultiPolygon
    ) -> shapely.geometry.MultiPolygon:
        epolys = []

        for poly in multipoly.geoms:
            line = shapely.geometry.LineString(poly.exterior)
            epoly = shapely.geometry.Polygon(line)

            epolys.append(epoly)

        return shapely.geometry.MultiPolygon(epolys)

    @classmethod
    def reorder_poly_points(
        cls, polygon: shapely.geometry.Polygon
    ) -> shapely.geometry.Polygon:
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

            holes.append(shapely.geometry.LineString(pts_ii))

        return shapely.geometry.Polygon(pts, holes=holes)

    @classmethod
    def fix_multipoly(
        cls, multipoly: shapely.geometry.MultiPolygon
    ) -> shapely.geometry.MultiPolygon:
        """ """
        valid_polys = []

        for poly in multipoly.geoms:
            if not poly.is_valid:
                fixed_poly = cls.fix_generic_polygon(poly)
                valid_polys.append(fixed_poly)
            else:
                valid_polys.append(poly)

        return shapely.geometry.MultiPolygon(valid_polys)

    @classmethod
    def fix_simple_polygon(
        cls, polygon: shapely.geometry.Polygon
    ) -> shapely.geometry.Polygon:
        """ """
        valid = make_valid(polygon)

        if valid.geom_type == "Polygon":
            return valid

        elif valid.geom_type == "MultiPolygon":
            # take the largest one! CHECKME
            largest_area = -1
            largest_poly = None
            for poly in valid.geoms:
                area = poly.area
                if area > largest_area:
                    largest_area = area
                    largest_poly = poly

            return largest_poly

        elif valid.geom_type == "GeometryCollection":
            # shit - FIXME  # take the largest Polygon
            largest_area = -1
            largest_poly = None

            for geom in valid.geoms:
                if geom.geom_type == "Polygon":
                    area = geom.area
                    if area > largest_area:
                        largest_area = area
                        largest_poly = geom
                elif geom.geom_type == "MultiLineString":
                    pass
                elif geom.geom_type == "LineString":
                    pass

            return largest_poly

        return None

    @classmethod
    def fix_generic_polygon(
        cls, polygon: shapely.geometry.Polygon
    ) -> shapely.geometry.Polygon:
        """
        fix exterior and interiors if not valid
        """
        if polygon.is_valid:
            return polygon

        exterior = polygon.exterior
        interiors = polygon.interiors

        ext_poly = shapely.geometry.Polygon(exterior)
        if not ext_poly.is_valid:
            ext_poly = cls.fix_simple_polygon(ext_poly)

        if not interiors:
            ext_linestring = shapely.geometry.LineString(ext_poly.exterior)

            fixed_poly = shapely.geometry.Polygon(ext_linestring)
        else:
            fixed_interiors: List[shapely.geometry.Polygon] = []
            for interior in interiors:
                int_poly = shapely.geometry.Polygon(interior)

                if not int_poly.is_valid:
                    int_poly = cls.fix_simple_polygon(int_poly)

                fixed_interiors.append(int_poly)

            ext_linestring = shapely.geometry.LineString(ext_poly.exterior)
            holes_linestrings = [
                shapely.geometry.LineString(int_poly.exterior)
                for int_poly in fixed_interiors
            ]

            fixed_poly = shapely.geometry.Polygon(
                ext_linestring, holes=holes_linestrings
            )

        return fixed_poly

    @classmethod
    def linearring_to_linestring(
        cls, linearring: shapely.geometry.LinearRing
    ) -> shapely.geometry.LineString:
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

            return shapely.geometry.LineString(coordinates)

        return shapely.geometry.LineString(linearring)

    @classmethod
    def dist(cls, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        return dx * dx + dy * dy
