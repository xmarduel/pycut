import os
import sys
import io

import shapely.geometry
import shapely

from shapely_svgpath_io import SvgPathDiscretizer
from shapely_svgpath_io import SvgPath

from shapely_matplotlib import MatplotLibUtils as pltutils

import unittest
from shapely_utils import ShapelyUtils
import xmlrunner


svg_circle = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg version="1.1" id="test_circle" width="100mm" height="100mm"  viewBox="0 0 100 100"
   xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">
  <g id="layer">
    <circle id="circle" style="fill:#007c00" cx="30" cy="30" r="5" />
  </g>
</svg>"""


svg_cubic_curve = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg version="1.1" id="test_circle" width="100mm" height="100mm"  viewBox="0 0 100 100"
   xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">
  <g id="layer">
<path id="contour" d="M 15.4080083203,40.9920221357 C 13.00000702,48.00002592 5.71700308718,44.0600237924 5.6850030699,49.9930269962 C 5.67300306342,55.9790302287 13.00000702,52.00002808 15.3970083144,58.9970318584 A 35.76,35.75 0 0,0 40.9920221357,84.6100456894 C 48.0040259222,87.0110469859 44.0320237773,94.2890509161 50.0380270205,94.3030509236 C 55.9940302368,94.3300509382 51.9890280741,87.0110469859 59.00003186,84.6160456926 A 35.75,35.75 0 0,0 84.6010456845,59.0040318622 C 87.00004698,52.00002808 94.3380509425,55.9200301968 94.3190509323,50.0280270151 C 94.3810509657,44.0070237638 87.00004698,48.00002592 84.600045684,40.9990221395 A 35.75,35.75 0 0,0 58.9960318578,15.4060083192 C 52.00002808,13.00000702 55.9900302346,5.70900308286 50.000027,5.72300309042 C 44.0110237659,5.64300304722 48.00002592,13.00000702 40.9990221395,15.4030083176 A 35.75,35.75 0 0,0 15.4080083203,40.9920221357 Z" style="fill:none;stroke:#00ff00;stroke-width:0.2"/>
  </g>
</svg>"""


OFFSET = 3.0


@unittest.skip("x")
class CircleOffsetTests_5_2(unittest.TestCase):
    """ """

    def setUp(self):
        """ """
        SvgPathDiscretizer.PYCUT_SAMPLE_LEN_COEFF = 5
        SvgPathDiscretizer.PYCUT_SAMPLE_MIN_NB_SEGMENTS = 2

    def tearDown(self):
        """ """

    # @unittest.skip("x")
    def test_offset_circle(self):
        """ """
        paths = SvgPath.svg_paths_from_svg_string(svg_circle)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        pts = path.discretize_closed_path()
        pltutils.plot(pts, "circle SvgElements")

        self.assertEqual(path.shape_tag, "circle")
        self.assertEqual(path.p_id, "circle")
        self.assertTrue(path.closed)

        self.assertEqual(len(pts), 157)

        # now the offset
        coordinates = [(complex_pt.real, complex_pt.imag) for complex_pt in pts]

        line = shapely.geometry.LineString(coordinates)

        offset = line.parallel_offset(OFFSET, "right", resolution=16)

        pltutils.plot_geom("offset CIRCLE", offset)

        self.assertEqual(offset.geom_type, "LineString")


@unittest.skip("x")
class CircleOffsetTests_10_5(unittest.TestCase):
    """ """

    def setUp(self):
        """ """
        SvgPathDiscretizer.PYCUT_SAMPLE_LEN_COEFF = 10
        SvgPathDiscretizer.PYCUT_SAMPLE_MIN_NB_SEGMENTS = 5

    def tearDown(self):
        """ """

    @unittest.skip("x")
    def test_offset_circle(self):
        """ """
        paths = SvgPath.svg_paths_from_svg_string(svg_circle)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        pts = path.discretize_closed_path()
        pltutils.plot(pts, "circle SvgElements")

        self.assertEqual(path.shape_tag, "circle")
        self.assertEqual(path.p_id, "circle")
        self.assertTrue(path.closed)

        self.assertEqual(len(pts), 313)

        # now the offset
        coordinates = [(complex_pt.real, complex_pt.imag) for complex_pt in pts]

        line = shapely.geometry.LineString(coordinates)

        offset = line.parallel_offset(OFFSET, "right", resolution=16)

        pltutils.plot_geom("offset CIRCLE", offset)

        self.assertEqual(offset.geom_type, "LineString")


# ----------------------------------------------------------------------
#
#
# ----------------------------------------------------------------------


@unittest.skip("x")
class CubicCurveOffsetTests_5_2(unittest.TestCase):
    """ """

    force_plot = True

    def setUp(self):
        """ """
        SvgPathDiscretizer.PYCUT_SAMPLE_LEN_COEFF = 5
        SvgPathDiscretizer.PYCUT_SAMPLE_MIN_NB_SEGMENTS = 2

    def tearDown(self):
        """ """

    @unittest.skip("x")
    def test_offset_left(self):
        """ """
        paths = SvgPath.svg_paths_from_svg_string(svg_cubic_curve)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        pts = path.discretize_closed_path()

        self.assertEqual(path.shape_tag, "path")
        self.assertEqual(path.p_id, "contour")
        self.assertTrue(path.closed)

        self.assertEqual(len(pts), 1325)

        # now the offset
        coordinates = [(complex_pt.real, complex_pt.imag) for complex_pt in pts]

        line = shapely.geometry.LineString(coordinates)

        offset = line.parallel_offset(
            OFFSET, "left", resolution=16, join_style=1, mitre_limit=5
        )

        if offset.geom_type != "LineString":
            pltutils.plot(pts, "contour")
            pltutils.plot_geom("offset LEFT", offset, force=self.force_plot)

        self.assertEqual(offset.geom_type, "LineString")

    # @unittest.skip("x")
    def test_offset_right_flip_ordering(self):
        """ """
        paths = SvgPath.svg_paths_from_svg_string(svg_cubic_curve)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        pts = path.discretize_closed_path()

        self.assertEqual(len(pts), 1325)  # (5,2)

        # now the offset / reverse first
        coordinates = [
            (complex_pt.real, complex_pt.imag) for complex_pt in reversed(list(pts))
        ]

        line = shapely.geometry.LineString(coordinates)

        offset = line.parallel_offset(
            OFFSET, "right", resolution=16, join_style=1, mitre_limit=5.0
        )

        if offset.geom_type != "LineString" or True:
            pltutils.plot(pts, "contour SvgElements")
            pltutils.plot_geom(
                "offset RIGHT of reversed", offset, force=self.force_plot
            )

        self.assertEqual(offset.geom_type, "LineString")

    @unittest.skip("x")
    def test_offset_left_as_linearring(self):
        """
        with open("linearring.txt", "w") as f:
           f.write(linearring.wkt)
        """
        paths = SvgPath.svg_paths_from_svg_string(svg_cubic_curve)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        pts = path.discretize_closed_path()

        self.assertEqual(len(pts), 1325)

        # now the offset
        # coordinates = [
        #    (complex_pt.real, complex_pt.imag) for complex_pt in reversed(list(pts))
        # ]
        coordinates = [(complex_pt.real, complex_pt.imag) for complex_pt in pts]

        linearring = shapely.geometry.LinearRing(coordinates)

        print("DEBUG  LINEARRING", len(linearring.coords))
        self.assertEqual(len(linearring.coords), 1326)

        offset = linearring.parallel_offset(
            OFFSET, "left", resolution=16, join_style=1, mitre_limit=5
        )

        print("OFFSET -> ", offset.geom_type)

        if offset.geom_type != "LineString":
            pltutils.plot_geom("LINEARRING", linearring, force=self.force_plot)
            pltutils.plot_geom("offset LINEARRING", offset, force=self.force_plot)

        if offset.geom_type == "MultiLineString":
            for linestring in offset.geoms:
                print("OFFSET MULTILINE part-line -> ", len(linestring.coords))

        self.assertEqual(offset.geom_type, "LineString")

    # @unittest.skip("x")
    def test_offset_left_as_poly_ext_no_orient(self):
        """with open("poly_ext.txt", "w") as f:
        f.write(poly_ext.wkt)
        """
        paths = SvgPath.svg_paths_from_svg_string(svg_cubic_curve)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        pts = path.discretize_closed_path()

        self.assertEqual(len(pts), 1325)

        # now the offset
        coordinates = [(complex_pt.real, complex_pt.imag) for complex_pt in pts]

        line = shapely.geometry.LineString(coordinates)
        poly = shapely.geometry.Polygon(line)

        poly_ext = poly.exterior

        print("DEBUG  LINE", len(line.coords))
        print("DEBUG  POLY-EXT", poly_ext.geom_type, len(poly_ext.coords))

        self.assertEqual(len(poly_ext.coords), 1326)

        offset = poly_ext.parallel_offset(
            OFFSET, "left", resolution=16, join_style=1, mitre_limit=5
        )

        if offset.geom_type != "LineString" or True:
            pltutils.plot_geom(
                "poly ext as linearring", poly_ext, force=self.force_plot
            )
            pltutils.plot_geom(
                "offset LEFT from poly_ext as linearring", offset, force=self.force_plot
            )

        self.assertEqual(offset.geom_type, "LineString")

    # @unittest.skip("x")
    def test_offset_right_as_poly_ext_orient(self):
        """ """
        paths = SvgPath.svg_paths_from_svg_string(svg_cubic_curve)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        pts = path.discretize_closed_path()

        self.assertEqual(len(pts), 1325)

        # now the offset
        coordinates = [(complex_pt.real, complex_pt.imag) for complex_pt in pts]

        line = shapely.geometry.LineString(coordinates)
        poly = shapely.geometry.Polygon(line)
        poly = shapely.geometry.polygon.orient(poly)

        poly_ext = poly.exterior

        print("DEBUG  LINE", len(line.coords))
        print("DEBUG  POLY-EXT", poly_ext.geom_type, len(poly_ext.coords))

        self.assertEqual(len(poly_ext.coords), 1326)

        offset = poly_ext.parallel_offset(
            OFFSET, "right", resolution=16, join_style=1, mitre_limit=5
        )

        if offset.geom_type != "LineString" or True:
            pltutils.plot_geom(
                "poly ext as linearring oriented", poly_ext, force=self.force_plot
            )
            pltutils.plot_geom(
                "offset RIGHT from poly_ext as linearring - poly oriented",
                offset,
                force=self.force_plot,
            )

        self.assertEqual(offset.geom_type, "LineString")


# @unittest.skip("x")
class CubicCurveOffsetTests_10_5(unittest.TestCase):
    """ """

    force_plot = True

    def setUp(self):
        """ """
        SvgPathDiscretizer.PYCUT_SAMPLE_LEN_COEFF = 10
        SvgPathDiscretizer.PYCUT_SAMPLE_MIN_NB_SEGMENTS = 5

    def tearDown(self):
        """ """

    @unittest.skip("x")
    def test_offset_left(self):
        """ """
        paths = SvgPath.svg_paths_from_svg_string(svg_cubic_curve)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        pts = path.discretize_closed_path()
        # pltutils.plot(pts, "contour")

        self.assertEqual(path.shape_tag, "path")
        self.assertEqual(path.p_id, "contour")
        self.assertTrue(path.closed)

        self.assertEqual(len(path.svgelt_path.segments()), 14)

        self.assertEqual(len(pts), 2653)

        # now the offset
        coordinates = [(complex_pt.real, complex_pt.imag) for complex_pt in pts]

        linestring = shapely.geometry.LineString(coordinates)

        print(
            "offset LEFT  linestring[0]=",
            linestring.coords.xy[0][0],
            linestring.coords.xy[1][0],
        )
        print(
            "offset LEFT  linestring[1]=",
            linestring.coords.xy[0][1],
            linestring.coords.xy[1][1],
        )
        print(
            "offset LEFT  linestring[2]=",
            linestring.coords.xy[0][2],
            linestring.coords.xy[1][2],
        )

        with open("linestring.txt", "w") as f:
            f.write(linestring.wkt)

        offset = linestring.parallel_offset(
            OFFSET, "left", resolution=16, join_style=1, mitre_limit=5
        )

        pltutils.plot_geom("offset LEFT", offset, force=True)

        self.assertEqual(offset.geom_type, "LineString")

    @unittest.skip("x")
    def test_offset_right_flip_ordering(self):
        """ """
        paths = SvgPath.svg_paths_from_svg_string(svg_cubic_curve)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        pts = path.discretize_closed_path()
        # pltutils.plot(pts, "contour")

        self.assertEqual(len(pts), 2653)

        # now the offset / reverse first
        coordinates = [
            (complex_pt.real, complex_pt.imag) for complex_pt in reversed(list(pts))
        ]

        linestring = shapely.geometry.LineString(coordinates)

        print(
            "offset RIGHT reversed  linestring[0]=",
            linestring.coords.xy[0][0],
            linestring.coords.xy[1][0],
        )
        print(
            "offset RIGHT reversed  linestring[1]=",
            linestring.coords.xy[0][1],
            linestring.coords.xy[1][1],
        )
        print(
            "offset RIGHT reversed  linestring[2]=",
            linestring.coords.xy[0][2],
            linestring.coords.xy[1][2],
        )

        with open("linestring_reversed.txt", "w") as f:
            f.write(linestring.wkt)

        offset = linestring.parallel_offset(
            OFFSET, "right", resolution=16, join_style=1, mitre_limit=5.0
        )

        pltutils.plot_geom("offset RIGHT of reversed", offset, force=True)

        self.assertEqual(offset.geom_type, "LineString")

    @unittest.skip("x")
    def test_offset_left_as_linearring(self):
        """ """
        paths = SvgPath.svg_paths_from_svg_string(svg_cubic_curve)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        pts = path.discretize_closed_path()

        self.assertEqual(len(pts), 2653)

        # now the offset
        coordinates = [(complex_pt.real, complex_pt.imag) for complex_pt in pts]

        linearring = shapely.geometry.LinearRing(coordinates)

        print("DEBUG  LINEARRING", len(linearring.coords))

        offset = linearring.parallel_offset(
            OFFSET, "left", resolution=16, join_style=1, mitre_limit=5
        )

        print("OFFSET -> ", offset.geom_type)

        if offset.geom_type != "LineString":
            pltutils.plot_geom("LINEARRING", linearring, force=self.force_plot)
            pltutils.plot_geom("offset LINEARRING", offset, force=self.force_plot)

        if offset.geom_type == "MultiLineString":
            for linestring in offset.geoms:
                print("OFFSET MULTILINE part-line -> ", len(linestring.coords))

        self.assertEqual(offset.geom_type, "LineString")

    @unittest.skip("x")
    def test_offset_left_as_poly_ext_no_orient(self):
        """ """
        paths = SvgPath.svg_paths_from_svg_string(svg_cubic_curve)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        pts = path.discretize_closed_path()

        self.assertEqual(len(pts), 2653)

        # now the offset
        coordinates = [(complex_pt.real, complex_pt.imag) for complex_pt in pts]

        line = shapely.geometry.LineString(coordinates)
        poly = shapely.geometry.Polygon(line)

        poly_ext = poly.exterior

        print("DEBUG  LINE", len(line.coords))
        print("DEBUG  POLY-EXT", poly_ext.geom_type, len(poly_ext.coords))

        self.assertEqual(len(poly_ext.coords), 2654)

        # with open("polyext_no_orient.txt", "w") as f:
        #    f.write(poly_ext.wkt)

        offset = poly_ext.parallel_offset(
            OFFSET, "left", resolution=16, join_style=1, mitre_limit=5
        )

        if offset.geom_type != "LineString" or True:
            pltutils.plot_geom(
                "poly ext (no orient)  as linearring", poly_ext, force=self.force_plot
            )
            pltutils.plot_geom(
                "offset LEFT from poly_ext (no orient) as linearring",
                offset,
                force=self.force_plot,
            )

        self.assertEqual(offset.geom_type, "LineString")

    @unittest.skip("x")
    def test_offset_right_as_poly_ext_orient(self):
        """
        GEOS BUG
        """
        paths = SvgPath.svg_paths_from_svg_string(svg_cubic_curve)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        pts = path.discretize_closed_path()

        self.assertEqual(len(pts), 2653)

        # now the offset
        coordinates = [(complex_pt.real, complex_pt.imag) for complex_pt in pts]

        line = shapely.geometry.LineString(coordinates)
        poly = shapely.geometry.Polygon(line)
        poly = shapely.geometry.polygon.orient(poly)

        poly_ext = poly.exterior

        print("DEBUG  LINE", len(line.coords))
        print("DEBUG  POLY-EXT", poly_ext.geom_type, len(poly_ext.coords))

        self.assertEqual(len(poly_ext.coords), 2654)

        # with open("polyext_orient.txt", "w") as f:
        #    f.write(poly_ext.wkt)

        offset = poly_ext.parallel_offset(
            OFFSET, "right", resolution=16, join_style=1, mitre_limit=5
        )

        if offset.geom_type != "LineString" or True:
            pltutils.plot_geom(
                "poly ext as linearring oriented", poly_ext, force=self.force_plot
            )
            pltutils.plot_geom(
                "offset RIGHT from poly_ext as linearring - poly oriented",
                offset,
                force=self.force_plot,
            )

        self.assertEqual(offset.geom_type, "LineString")

    # @unittest.skip("x")
    def test_offset_right_as_poly_ext_orient_as_linestring(self):
        """
        transform the poly_ext (which is a linearring) as linestring (remove last point)
        GEOS GOOD!
        """
        paths = SvgPath.svg_paths_from_svg_string(svg_cubic_curve)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        pts = path.discretize_closed_path()

        self.assertEqual(len(pts), 2653)

        # now the offset
        coordinates = [(complex_pt.real, complex_pt.imag) for complex_pt in pts]

        line = shapely.geometry.LineString(coordinates)
        poly = shapely.geometry.Polygon(line)
        poly = shapely.geometry.polygon.orient(poly)

        poly_ext = poly.exterior

        print("DEBUG  LINE", len(line.coords))
        print("DEBUG  POLY-EXT", poly_ext.geom_type, len(poly_ext.coords))

        self.assertEqual(len(poly_ext.coords), 2654)

        # with open("polyext_orient.txt", "w") as f:
        #    f.write(poly_ext.wkt)

        linestring = ShapelyUtils.linearring_to_linestring(poly_ext)

        self.assertEqual(len(linestring.coords), 2653)

        offset = linestring.parallel_offset(
            OFFSET, "right", resolution=16, join_style=1, mitre_limit=5
        )

        if offset.geom_type != "LineString" or True:
            pltutils.plot_geom(
                "poly ext as linearring oriented", poly_ext, force=self.force_plot
            )
            pltutils.plot_geom(
                "offset RIGHT from poly_ext (oriented) as linestring from linearring",
                offset,
                force=self.force_plot,
            )

        self.assertEqual(offset.geom_type, "LineString")


def get_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(CircleOffsetTests_5_2))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(CircleOffsetTests_10_5))
    suite.addTest(
        unittest.TestLoader().loadTestsFromTestCase(CubicCurveOffsetTests_5_2)
    )
    suite.addTest(
        unittest.TestLoader().loadTestsFromTestCase(CubicCurveOffsetTests_10_5)
    )

    return suite


if __name__ == "__main__":
    if os.environ.get("PYCUT_XMLRUNNER_UNITTESTS", None) == "YES":
        unittest.main(
            testRunner=xmlrunner.XMLTestRunner(
                path="RESULTS", indic="test_shapely_offset"
            )
        )
    else:
        unittest.main()


# unittest.TextTestRunner(verbosity=2).run(suite)
# xmlrunner.XMLTestRunner(path='RESULTS', indic="test_svgpath_discretise").run(get_suite()[0])
