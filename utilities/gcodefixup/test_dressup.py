import math
import unittest

from utilities.gcodefixup.gcode_dressup import GCodePatternDressUp
from utilities.gcodefixup.gcode_dressup import Point

cutter_radius = 1.0


class TestSum(unittest.TestCase):
    """ """

    def setUp(self):
        self.cutter_radius = 1.0

    def test_1(self):
        pt1 = Point(-2.0, 2.0)
        ptc = Point(4.0, 4.0)
        pt2 = Point(2.0, -2.0)

        ff = GCodePatternDressUp(self.cutter_radius, pt1, ptc, pt2)
        res = ff.make_dressup()

        print(res)

        self.assertAlmostEqual(
            ff.bisect_ok, math.pi / 4.0, places=4, msg="Should be pi/4.0"
        )

    def test_2(self):
        pt1 = Point(2.0, 2.0)
        ptc = Point(-4.0, 4.0)
        pt2 = Point(-2.0, -2.0)

        ff = GCodePatternDressUp(self.cutter_radius, pt1, ptc, pt2)
        res = ff.make_dressup()

        print(res)

        self.assertAlmostEqual(
            ff.bisect_ok, 3 * math.pi / 4.0, places=4, msg="Should be 3*pi/4.0"
        )

    def test_3(self):
        """
        *-------*
        |
        |
        +
        """
        pt1 = Point(+0.001, 0.0)
        ptc = Point(0.0, 4.0)
        pt2 = Point(4.0, 4.0)

        ff = GCodePatternDressUp(self.cutter_radius, pt1, ptc, pt2)
        res = ff.make_dressup()

        print(res)

        self.assertAlmostEqual(
            ff.bisect_ok, 3 * math.pi / 4.0, places=3, msg="Should be 3*pi/4.0"
        )

    def test_4(self):
        """
        *-------*
        |
        |
        +
        """
        pt1 = Point(-0.001, 0.0)
        ptc = Point(0.0, 4.0)
        pt2 = Point(4.0, 4.0)

        ff = GCodePatternDressUp(self.cutter_radius, pt1, ptc, pt2)
        res = ff.make_dressup()

        print(res)

        self.assertAlmostEqual(
            ff.bisect_ok, 3 * math.pi / 4.0, places=3, msg="Should be 3*pi/4.0"
        )

    def test_5(self):
        """
        *-------*
        |
        |
        +
        """
        pt1 = Point(0.0, 0.0)
        ptc = Point(0.0, 4.0)
        pt2 = Point(4.0, 4.0)

        ff = GCodePatternDressUp(self.cutter_radius, pt1, ptc, pt2)
        res = ff.make_dressup()

        print(res)

        self.assertAlmostEqual(
            ff.bisect_ok, 3 * math.pi / 4.0, places=4, msg="Should be 3*pi/4.0"
        )

    def test_6(self):
        """
              *
            /   \
          /       \
        +           +
        """
        pt1 = Point(-4.0, 0.0)
        ptc = Point(0.0, 4.0)
        pt2 = Point(4.0, 0.0)

        ff = GCodePatternDressUp(self.cutter_radius, pt1, ptc, pt2)
        res = ff.make_dressup()

        print(res)

        self.assertAlmostEqual(
            ff.bisect_ok, math.pi / 2.0, places=4, msg="Should be pi/2.0"
        )

    def test_6b(self):
        """
              *
            /   \
          /       \
        +           +
        """
        pt1 = Point(-4.0, 0.0).scale(0.01)
        ptc = Point(0.0, 4.0).scale(0.01)
        pt2 = Point(4.0, 0.0).scale(0.01)

        ff = GCodePatternDressUp(self.cutter_radius, pt1, ptc, pt2)
        res = ff.make_dressup()

        print(res)

        self.assertAlmostEqual(
            ff.bisect_ok, math.pi / 2.0, places=4, msg="Should be pi/2.0"
        )

    def test_7(self):
        """
        *           *
          \       /
            \   /
              +
        """
        pt1 = Point(-4.0, 0.0)
        ptc = Point(0.0, -4.0)
        pt2 = Point(4.0, 0.0)

        ff = GCodePatternDressUp(self.cutter_radius, pt1, ptc, pt2)
        res = ff.make_dressup()

        print(res)

        self.assertAlmostEqual(
            ff.bisect_ok, 3 * math.pi / 2.0, places=4, msg="Should be 3*pi/2.0"
        )

    def test_7b(self):
        """
        *           *
          \       /
            \   /
              +
        """
        pt1 = Point(-4.0, 0.0).scale(0.01)
        ptc = Point(0.0, -4.0).scale(0.01)
        pt2 = Point(4.0, 0.0).scale(0.01)

        ff = GCodePatternDressUp(self.cutter_radius, pt1, ptc, pt2)
        res = ff.make_dressup()

        print(res)

        self.assertAlmostEqual(
            ff.bisect_ok, 3 * math.pi / 2.0, places=4, msg="Should be 3*pi/2.0"
        )


if __name__ == "__main__":
    unittest.main()
