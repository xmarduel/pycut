import os
import sys
import io

from shapely_svgpath_io import SvgPathDiscretizer
from shapely_svgpath_io import SvgPath

import unittest
import xmlrunner

import matplotlib.pyplot as plt


svg_rect = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg version="1.1" id="test_rectangle" width="100mm" height="100mm" viewBox="0 0 100 100"
   xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">
  <g id="layer">
     <rect id="rect" style="fill:#0000ff" width="50" height="70" x="10" y="10" rx="5" ry="5" />
  </g>
</svg>"""

svg_circle = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg version="1.1" id="test_circle" width="100mm" height="100mm"  viewBox="0 0 100 100"
   xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">
  <g id="layer">
    <circle id="circle" style="fill:#007c00" cx="30" cy="30" r="5" />
  </g>
</svg>"""

svg_ellipse = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg version="1.1" id="test_ellipse" width="100mm" height="100mm"  viewBox="0 0 100 100"
   xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">
  <g id="layer">
    <ellipse id="ellipse" cx="100" cy="50" rx="100" ry="50" />
  </g>
</svg>"""

svg_line = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg version="1.1" id="test_line" width="100mm" height="100mm"  viewBox="0 0 100 100"
   xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">
  <g id="layer">
    <line id="line" x1="10" y1="10" x2="80" y2="60" stroke="black"/>
  </g>
</svg>"""

svg_polyline = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg version="1.1" id="test_polyline" width="300mm" height="300mm"  viewBox="0 0 300 300"
   xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">
  <g id="layer">
    <polyline id="polyline" points="100,100 150,25 150,75 200,0" fill="none" stroke="black" />
  </g>
</svg>"""

svg_polygon1 = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg version="1.1" id="test_polygon" width="300mm" height="300mm"  viewBox="0 0 300 300"
   xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">
  <g id="layer">
    <polygon id="polygon1" points="100,100 200,100 150,150 100,100" fill="none" stroke="black" />
  </g>
</svg>"""

svg_polygon2 = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg version="1.1" id="test_polygon" width="300mm" height="300mm"  viewBox="0 0 300 300"
   xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">
  <g id="layer">
    <polygon id="polygon2" points="100,100 200,100 150,150" fill="none" stroke="black" />
  </g>
</svg>"""

svg_path = """<?xml version='1.0' encoding='UTF-8'?>
<svg version="1.1" id="spindle-D55-holder-with-clamp"
  xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg" width="140mm" height="113mm" viewBox="0 0 140 113">
  <g id="layer">
    <path id="contour" d="M 21.00001134,0 l 88.00004752,0 a 1,1 0 0,1 1.00000054,1.00000054 l 0,48.00002592 a 1,1 0 0,0 1.00000054,1.00000054 l 12.00000648,0 a 1,1 0 0,1 1.00000054,1.00000054 l 0,38.00002052 a 1,1 0 0,1 -1.00000054,1.00000054 l -18.700010098,0 A 45,45 0 0,1 25.700013878,90.0000486 l -18.700010098,0 a 1,1 0 0,1 -1.00000054,-1.00000054 l 0,-38.00002052 a 1,1 0 0,1 1.00000054,-1.00000054 l 12.00000648,0 a 1,1 0 0,0 1.00000054,-1.00000054 l 0,-48.00002592 a 1,1 0 0,1 1.00000054,-1.00000054 z" style="fill:none;stroke:#0000ff;stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"/>
  </g>
</svg>
"""

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


class SvgElementsTests(unittest.TestCase):
    """ """

    def setUp(self):
        SvgPathDiscretizer.PYCUT_SAMPLE_LEN_COEFF = 10
        SvgPathDiscretizer.PYCUT_SAMPLE_MIN_NB_SEGMENTS = 5

    def tearDown(self):
        pass

    def test_discretise_rectangle(self):
        """ """
        paths = SvgPath.svg_paths_from_svg_string(svg_rect)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        self.assertEqual(path.shape_tag, "rect")
        self.assertEqual(path.p_id, "rect")
        self.assertEqual(path.closed, True)

        print("RECT len = ", path.svgelt_path.length())

        self.assertEqual(len(path.svgelt_path.segments()), 10)
        self.assertEqual(path.svgelt_path.segments()[0].__class__.__name__, "Move")
        self.assertEqual(path.svgelt_path.segments()[1].__class__.__name__, "Line")
        self.assertEqual(path.svgelt_path.segments()[2].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path.segments()[3].__class__.__name__, "Line")
        self.assertEqual(path.svgelt_path.segments()[4].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path.segments()[5].__class__.__name__, "Line")
        self.assertEqual(path.svgelt_path.segments()[6].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path.segments()[7].__class__.__name__, "Line")
        self.assertEqual(path.svgelt_path.segments()[8].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path.segments()[9].__class__.__name__, "Close")

        pts = path.discretize_closed_path()

        self.assertEqual(len(pts), 317)

    def test_discretise_circle(self):
        """ """
        paths = SvgPath.svg_paths_from_svg_string(svg_circle)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        self.assertEqual(path.shape_tag, "circle")
        self.assertEqual(path.p_id, "circle")
        self.assertEqual(path.closed, True)

        print("CIRCLE len = ", path.svgelt_path.length())

        self.assertEqual(len(path.svgelt_path.segments()), 6)
        self.assertEqual(path.svgelt_path.segments()[0].__class__.__name__, "Move")
        self.assertEqual(path.svgelt_path.segments()[1].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path.segments()[2].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path.segments()[3].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path.segments()[4].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path.segments()[5].__class__.__name__, "Close")

        pts = path.discretize_closed_path()

        # not the same #pts as in svgpathtools because 4 arcs and rounding stuff
        # plot(pts, "circle SvgElements")

        self.assertEqual(len(pts), 313)

    def test_discretise_ellipse(self):
        """ """
        paths = SvgPath.svg_paths_from_svg_string(svg_ellipse)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        self.assertEqual(path.shape_tag, "ellipse")
        self.assertEqual(path.p_id, "ellipse")
        self.assertEqual(path.closed, True)

        print("ELLIPSE len = ", path.svgelt_path.length())

        self.assertEqual(len(path.svgelt_path.segments()), 6)
        self.assertEqual(path.svgelt_path.segments()[0].__class__.__name__, "Move")
        self.assertEqual(path.svgelt_path.segments()[1].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path.segments()[2].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path.segments()[3].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path.segments()[4].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path.segments()[5].__class__.__name__, "Close")

        pts = path.discretize_closed_path()

        self.assertEqual(len(pts), 4845)

    def test_discretise_line(self):
        """ """
        paths = SvgPath.svg_paths_from_svg_string(svg_line)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        self.assertEqual(path.shape_tag, "line")
        self.assertEqual(path.p_id, "line")
        self.assertEqual(path.closed, False)

        print("LINE len = ", path.svgelt_path.length())

        self.assertEqual(len(path.svgelt_path.segments()), 2)
        self.assertEqual(path.svgelt_path.segments()[0].__class__.__name__, "Move")
        self.assertEqual(path.svgelt_path.segments()[1].__class__.__name__, "Line")

        pts = path.discretize_open_path()

        self.assertEqual(len(pts), 2)

    def test_discretise_polyline(self):
        """ """
        paths = SvgPath.svg_paths_from_svg_string(svg_polyline)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        self.assertEqual(path.shape_tag, "polyline")
        self.assertEqual(path.p_id, "polyline")
        self.assertEqual(path.closed, False)

        print("POLYLINE len = ", path.svgelt_path.length())

        self.assertEqual(len(path.svgelt_path.segments()), 4)
        self.assertEqual(path.svgelt_path.segments()[0].__class__.__name__, "Move")
        self.assertEqual(path.svgelt_path.segments()[1].__class__.__name__, "Line")
        self.assertEqual(path.svgelt_path.segments()[2].__class__.__name__, "Line")
        self.assertEqual(path.svgelt_path.segments()[3].__class__.__name__, "Line")

        pts = path.discretize_open_path()

        self.assertEqual(len(pts), 4)

    def test_discretise_polygon1(self):
        """ """
        paths = SvgPath.svg_paths_from_svg_string(svg_polygon1)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        self.assertEqual(path.shape_tag, "polygon")
        self.assertEqual(path.p_id, "polygon1")
        self.assertEqual(path.closed, True)

        print("POLYGON-1 len = ", path.svgelt_path.length())

        self.assertEqual(len(path.svgelt_path.segments()), 5)
        self.assertEqual(path.svgelt_path.segments()[0].__class__.__name__, "Move")
        self.assertEqual(path.svgelt_path.segments()[1].__class__.__name__, "Line")
        self.assertEqual(path.svgelt_path.segments()[2].__class__.__name__, "Line")
        self.assertEqual(path.svgelt_path.segments()[3].__class__.__name__, "Line")
        self.assertEqual(path.svgelt_path.segments()[4].__class__.__name__, "Close")

        pts = path.discretize_closed_path()
        """
        expecting 4 points (not 3) because of the shapely fix
        """
        self.assertEqual(len(pts), 4)

    def test_discretise_polygon2(self):
        """ """
        paths = SvgPath.svg_paths_from_svg_string(svg_polygon2)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        self.assertEqual(path.shape_tag, "polygon")
        self.assertEqual(path.p_id, "polygon2")
        self.assertEqual(path.closed, True)

        print("POLYGON-2 len = ", path.svgelt_path.length())

        self.assertEqual(len(path.svgelt_path.segments()), 4)
        # yes , only 2 lines, hopefully the discretisation is ok...
        self.assertEqual(path.svgelt_path.segments()[0].__class__.__name__, "Move")
        self.assertEqual(path.svgelt_path.segments()[1].__class__.__name__, "Line")
        self.assertEqual(path.svgelt_path.segments()[2].__class__.__name__, "Line")
        self.assertEqual(path.svgelt_path.segments()[3].__class__.__name__, "Close")

        pts = path.discretize_closed_path()
        """
        expecting 4 points (not 3) because of the shapely fix
        """
        self.assertEqual(len(pts), 4)

    def test_discretise_path(self):
        """
        no end point, start point
        """
        paths = SvgPath.svg_paths_from_svg_string(svg_path)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        self.assertEqual(path.shape_tag, "path")
        self.assertEqual(path.p_id, "contour")
        self.assertEqual(path.closed, True)

        print("PATH len = ", path.svgelt_path.length())

        self.assertEqual(len(path.svgelt_path.segments()), 20)
        self.assertEqual(path.svgelt_path[0].__class__.__name__, "Move")
        self.assertEqual(path.svgelt_path[1].__class__.__name__, "Line")
        self.assertEqual(path.svgelt_path[2].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path[3].__class__.__name__, "Line")
        self.assertEqual(path.svgelt_path[4].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path[5].__class__.__name__, "Line")
        self.assertEqual(path.svgelt_path[6].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path[7].__class__.__name__, "Line")
        self.assertEqual(path.svgelt_path[8].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path[9].__class__.__name__, "Line")
        self.assertEqual(path.svgelt_path[10].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path[11].__class__.__name__, "Line")
        self.assertEqual(path.svgelt_path[12].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path[13].__class__.__name__, "Line")
        self.assertEqual(path.svgelt_path[14].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path[15].__class__.__name__, "Line")
        self.assertEqual(path.svgelt_path[16].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path[17].__class__.__name__, "Line")
        self.assertEqual(path.svgelt_path[18].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path[19].__class__.__name__, "Close")

        pts = path.discretize_closed_path()
        self.assertEqual(len(pts), 1085)

        # plot(pts, "path SvgElements")

    def test_discretise_cubic_curve(self):
        """
        no end point, start point
        """
        paths = SvgPath.svg_paths_from_svg_string(svg_cubic_curve)

        self.assertEqual(len(paths), 1)
        path = paths[0]

        self.assertEqual(path.shape_tag, "path")
        self.assertEqual(path.p_id, "contour")
        self.assertEqual(path.closed, True)

        print("CUBIC-CURVE len = ", path.svgelt_path.length())

        self.assertEqual(len(path.svgelt_path.segments()), 14)
        self.assertEqual(path.svgelt_path.segments()[0].__class__.__name__, "Move")
        self.assertEqual(
            path.svgelt_path.segments()[1].__class__.__name__, "CubicBezier"
        )
        self.assertEqual(
            path.svgelt_path.segments()[2].__class__.__name__, "CubicBezier"
        )
        self.assertEqual(path.svgelt_path.segments()[3].__class__.__name__, "Arc")
        self.assertEqual(
            path.svgelt_path.segments()[4].__class__.__name__, "CubicBezier"
        )
        self.assertEqual(
            path.svgelt_path.segments()[5].__class__.__name__, "CubicBezier"
        )
        self.assertEqual(path.svgelt_path.segments()[6].__class__.__name__, "Arc")
        self.assertEqual(
            path.svgelt_path.segments()[7].__class__.__name__, "CubicBezier"
        )
        self.assertEqual(
            path.svgelt_path.segments()[8].__class__.__name__, "CubicBezier"
        )
        self.assertEqual(path.svgelt_path.segments()[9].__class__.__name__, "Arc")
        self.assertEqual(
            path.svgelt_path.segments()[10].__class__.__name__, "CubicBezier"
        )
        self.assertEqual(
            path.svgelt_path.segments()[11].__class__.__name__, "CubicBezier"
        )
        self.assertEqual(path.svgelt_path.segments()[12].__class__.__name__, "Arc")
        self.assertEqual(path.svgelt_path.segments()[13].__class__.__name__, "Close")

        pts = path.discretize_closed_path()
        self.assertEqual(len(pts), 2653)

        # plot(pts, "path SvgElements")


def get_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(SvgElementsTests))

    return suite


if __name__ == "__main__":
    if os.environ.get("PYCUT_XMLRUNNER_UNITTESTS", None) == "YES":
        unittest.main(
            testRunner=xmlrunner.XMLTestRunner(
                path="RESULTS", indic="test_svgpath_discretise"
            )
        )
    else:
        unittest.main()


# unittest.TextTestRunner(verbosity=2).run(suite)
# xmlrunner.XMLTestRunner(path='RESULTS', indic="test_svgpath_discretise").run(get_suite()[0])
