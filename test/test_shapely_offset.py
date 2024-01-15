import os
import sys
import io

import shapely.geometry
import matplotlib.pyplot as plt

from svgpath_svgelements import SvgPath_SvgElements

import unittest
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


def plot(pts, title):
    plt.figure()
    plt.title(title)

    xx = [pt.real for pt in pts]
    yy = [pt.imag for pt in pts]

    plt.plot(xx, yy, "ro-")

    plt.axis("equal")
    plt.show()


class ShapelyLineStringOffsetTests(unittest.TestCase):
    """ """

    def setUp(self):
        """ """
        pass

    def tearDown(self):
        """ """

    def xtest_offset_circle(self):
        """ """
        paths = SvgPath_SvgElements.read_paths_from_file(io.StringIO(svg_circle))

        self.assertEqual(len(paths), 1)

        path = paths[0]

        self.assertEqual(path.tag, "circle")
        self.assertEqual(path.p_id, "circle")
        self.assertTrue(path.closed)

        self.assertEqual(len(path.svg_path.segments()), 6)
        self.assertEqual(path.svg_path.segments()[0].__class__.__name__, "Move")
        self.assertEqual(path.svg_path.segments()[1].__class__.__name__, "Arc")
        self.assertEqual(path.svg_path.segments()[2].__class__.__name__, "Arc")
        self.assertEqual(path.svg_path.segments()[3].__class__.__name__, "Arc")
        self.assertEqual(path.svg_path.segments()[4].__class__.__name__, "Arc")
        self.assertEqual(path.svg_path.segments()[5].__class__.__name__, "Close")

        pts = path.discretize_closed_path()
        plot(pts, "circle SvgElements")

        self.assertEqual(len(pts), 313)

        # now the offset
        coordinates = [(complex_pt.real, complex_pt.imag) for complex_pt in pts]

        line = shapely.geometry.LineString(coordinates)

        offset = line.parallel_offset(5.0, "right", resolution=16)
        offset_lines = []

        if offset.geom_type == "LineString":
            offset_lines.append(offset)
        elif offset.geom_type == "MultiLineString":
            for line in offset.geoms:
                if line.is_empty:
                    continue
                offset_lines.append(line)

        for offset_line in offset_lines:
            x = offset_line.coords.xy[0]
            y = offset_line.coords.xy[1]

            pts = [(pt_x + pt_y * 1j) for (pt_x, pt_y) in zip(x, y)]

            plot(pts, "circle offset")

    def xtest_offset_cubic_curve_left(self):
        """ """
        paths = SvgPath_SvgElements.read_paths_from_file(io.StringIO(svg_cubic_curve))

        self.assertEqual(len(paths), 1)

        path = paths[0]

        self.assertEqual(path.tag, "path")
        self.assertEqual(path.p_id, "contour")
        self.assertTrue(path.closed)

        self.assertEqual(len(path.svg_path.segments()), 14)
        self.assertEqual(path.svg_path.segments()[0].__class__.__name__, "Move")
        self.assertEqual(path.svg_path.segments()[1].__class__.__name__, "CubicBezier")
        self.assertEqual(path.svg_path.segments()[2].__class__.__name__, "CubicBezier")
        self.assertEqual(path.svg_path.segments()[3].__class__.__name__, "Arc")
        self.assertEqual(path.svg_path.segments()[4].__class__.__name__, "CubicBezier")
        self.assertEqual(path.svg_path.segments()[5].__class__.__name__, "CubicBezier")
        self.assertEqual(path.svg_path.segments()[6].__class__.__name__, "Arc")
        self.assertEqual(path.svg_path.segments()[7].__class__.__name__, "CubicBezier")
        self.assertEqual(path.svg_path.segments()[8].__class__.__name__, "CubicBezier")
        self.assertEqual(path.svg_path.segments()[9].__class__.__name__, "Arc")
        self.assertEqual(path.svg_path.segments()[10].__class__.__name__, "CubicBezier")
        self.assertEqual(path.svg_path.segments()[11].__class__.__name__, "CubicBezier")
        self.assertEqual(path.svg_path.segments()[12].__class__.__name__, "Arc")
        self.assertEqual(path.svg_path.segments()[13].__class__.__name__, "Close")

        print(path)

        pts = path.discretize_closed_path()
        plot(pts, "contour SvgElements")

        self.assertEqual(len(pts), 2653)

        # now the offset
        coordinates = [(complex_pt.real, complex_pt.imag) for complex_pt in pts]

        line = shapely.geometry.LineString(coordinates)

        offset = line.parallel_offset(
            4.0, "left", resolution=16, join_style=1, mitre_limit=5.0
        )
        offset_lines = []

        if offset.geom_type == "LineString":
            print("OFFSET -> LINE")
            offset_lines.append(offset)
        elif offset.geom_type == "MultiLineString":
            print("OFFSET -> MULTILINE")
            for line in offset.geoms:
                if line.is_empty:
                    continue
                offset_lines.append(line)

        for offset_line in offset_lines:
            x = offset_line.coords.xy[0]
            y = offset_line.coords.xy[1]

            pts = [(pt_x + pt_y * 1j) for (pt_x, pt_y) in zip(x, y)]

            plot(pts, "circle offset")

    def test_offset_cubic_curve_right(self):
        """ """
        paths = SvgPath_SvgElements.read_paths_from_file(io.StringIO(svg_cubic_curve))

        self.assertEqual(len(paths), 1)

        path = paths[0]

        self.assertEqual(path.tag, "path")
        self.assertEqual(path.p_id, "contour")
        self.assertTrue(path.closed)

        self.assertEqual(len(path.svg_path.segments()), 14)
        self.assertEqual(path.svg_path.segments()[0].__class__.__name__, "Move")
        self.assertEqual(path.svg_path.segments()[1].__class__.__name__, "CubicBezier")
        self.assertEqual(path.svg_path.segments()[2].__class__.__name__, "CubicBezier")
        self.assertEqual(path.svg_path.segments()[3].__class__.__name__, "Arc")
        self.assertEqual(path.svg_path.segments()[4].__class__.__name__, "CubicBezier")
        self.assertEqual(path.svg_path.segments()[5].__class__.__name__, "CubicBezier")
        self.assertEqual(path.svg_path.segments()[6].__class__.__name__, "Arc")
        self.assertEqual(path.svg_path.segments()[7].__class__.__name__, "CubicBezier")
        self.assertEqual(path.svg_path.segments()[8].__class__.__name__, "CubicBezier")
        self.assertEqual(path.svg_path.segments()[9].__class__.__name__, "Arc")
        self.assertEqual(path.svg_path.segments()[10].__class__.__name__, "CubicBezier")
        self.assertEqual(path.svg_path.segments()[11].__class__.__name__, "CubicBezier")
        self.assertEqual(path.svg_path.segments()[12].__class__.__name__, "Arc")
        self.assertEqual(path.svg_path.segments()[13].__class__.__name__, "Close")

        print(path)

        pts = path.discretize_closed_path()
        plot(pts, "contour SvgElements")

        self.assertEqual(len(pts), 2653)

        # now the offset
        coordinates = [(complex_pt.real, complex_pt.imag) for complex_pt in pts]

        line = shapely.geometry.LineString(coordinates)

        offset = line.parallel_offset(
            4.0, "right", resolution=16, join_style=1, mitre_limit=5.0
        )
        offset_lines = []

        if offset.geom_type == "LineString":
            print("OFFSET -> LINE")
            offset_lines.append(offset)
        elif offset.geom_type == "MultiLineString":
            print("OFFSET -> MULTILINE")
            for line in offset.geoms:
                if line.is_empty:
                    continue
                offset_lines.append(line)

        for offset_line in offset_lines:
            x = offset_line.coords.xy[0]
            y = offset_line.coords.xy[1]

            pts = [(pt_x + pt_y * 1j) for (pt_x, pt_y) in zip(x, y)]

            plot(pts, "circle offset")


def get_suite():
    suite = unittest.TestSuite()
    suite.addTest(
        unittest.TestLoader().loadTestsFromTestCase(ShapelyLineStringOffsetTests)
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
