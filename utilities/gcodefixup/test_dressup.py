import math
import unittest

from utilities.gcodefixup.gcode_dressup import GCodePatternDressUp

cutter_radius = 1.0


class TestSum(unittest.TestCase):
    """ """

    def setUp(self):
        self.cutter_radius = 1.0

    def test_1(self):
        v = [-2.0, 2.0, 4.0, 4.0, 2.0, -2.0]
        ff = GCodePatternDressUp(self.cutter_radius, v[0], v[1], v[2], v[3], v[4], v[5])
        res = ff.make_dressup()

        print(res)

        self.assertAlmostEqual(ff.bisect_ok, math.pi / 4.0, places=4, msg="Should be pi/4.0")

    def test_2(self):
        v = [2.0, 2.0, -4.0, 4.0, -2.0, -2.0]
        ff = GCodePatternDressUp(self.cutter_radius, v[0], v[1], v[2], v[3], v[4], v[5])
        res = ff.make_dressup()

        print(res)

        self.assertAlmostEqual(ff.bisect_ok, 3 * math.pi / 4.0, places=4, msg="Should be 3*pi/4.0")

    def test_3(self):
        """
        *-------*
        |
        |
        +
        """
        v = [+0.001, 0.0, 0.0, 4.0, 4.0, 4.0]
        ff = GCodePatternDressUp(self.cutter_radius, v[0], v[1], v[2], v[3], v[4], v[5])
        res = ff.make_dressup()

        print(res)

        self.assertAlmostEqual(ff.bisect_ok, 3 * math.pi / 4.0, places=3, msg="Should be 3*pi/4.0")

    def test_4(self):
        """
        *-------*
        |
        |
        +
        """
        v = [-0.001, 0.0, 0.0, 4.0, 4.0, 4.0]
        ff = GCodePatternDressUp(self.cutter_radius, v[0], v[1], v[2], v[3], v[4], v[5])
        res = ff.make_dressup()

        print(res)

        self.assertAlmostEqual(ff.bisect_ok, 3 * math.pi / 4.0, places=3, msg="Should be 3*pi/4.0")

    def test_5(self):
        """
        *-------*
        |
        |
        +
        """
        v = [0.0, 0.0, 0.0, 4.0, 4.0, 4.0]
        ff = GCodePatternDressUp(self.cutter_radius, v[0], v[1], v[2], v[3], v[4], v[5])
        res = ff.make_dressup()

        print(res)

        self.assertAlmostEqual(ff.bisect_ok, 3 * math.pi / 4.0, places=4, msg="Should be 3*pi/4.0")

    def test_6(self):
        """
              *
            /   \
          /       \
        +           +
        """
        v = [-4.0, 0.0, 0.0, 4.0, 4.0, 0.0]
        ff = GCodePatternDressUp(self.cutter_radius, v[0], v[1], v[2], v[3], v[4], v[5])
        res = ff.make_dressup()

        print(res)

        self.assertAlmostEqual(ff.bisect_ok, math.pi / 2.0, places=4, msg="Should be pi/2.0")

    def test_7(self):
        """
        *           *
          \       /
            \   /
              +
        """
        v = [-4.0, 0.0, 0.0, -4.0, 4.0, 0.0]
        ff = GCodePatternDressUp(self.cutter_radius, v[0], v[1], v[2], v[3], v[4], v[5])
        res = ff.make_dressup()

        print(res)

        self.assertAlmostEqual(ff.bisect_ok, 3 * math.pi / 2.0, places=4, msg="Should be 3*pi/2.0")


if __name__ == "__main__":
    unittest.main()
