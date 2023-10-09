VERSION = "0_1_0"

import argparse
from math import *
from typing import Tuple

import shapely.geometry
import shapely.ops


def RAD_TO_DEG(val):
    return val * 180.0 / pi


class GCodePatternDressUp:
    """ """

    def __init__(
        self,
        cutter_radius: float,
        x1: float,
        y1: float,
        xc: float,
        yc: float,
        x2: float,
        y2: float,
    ):
        """
        From

        G1 X<xo> Y<yo>
        G1 X<xc> Y<yc>
        G1 X<x2> Y<y2>

        segment [X1:C]:  a1.x + b1.y + c1 = 0
        segment [X2:C]:  a2.x + b2.y + c2 = 0

        """
        self.cutter_radius = cutter_radius

        # the points
        self.x1 = x1
        self.y1 = y1
        self.xc = xc
        self.yc = yc
        self.x2 = x2
        self.y2 = y2

        # slopes of the segments : y = mx + b  or ax + by + c = 0
        if xc != x1:
            self.a1 = (yc - y1) / (xc - x1)
            self.b1 = -1.0
            self.c1 = -(self.a1 * self.xc + self.b1 * self.yc)

        else:
            self.a1 = 1.0
            self.b1 = 0.0
            self.c1 = -(self.a1 * self.xc + self.b1 * self.yc)

        if x2 != xc:
            self.a2 = (y2 - yc) / (x2 - xc)
            self.b2 = -1.0
            self.c2 = -(self.a2 * self.xc + self.b2 * self.yc)
        else:
            self.a2 = 1.0
            self.b2 = 0.0
            self.c2 = -(self.a2 * self.xc + self.b2 * self.yc)

        self.corner_angle = self.calc_corner_angle()
        self.gap = self.calc_gap()

        self.bisect1, self.bisect2, self.bisect_ok = self.calc_bisection_angles()

        self.dx, self.dy = self.calc_dx_dy()

    @classmethod
    def norm_vec(cls, vec) -> float:
        return sqrt(vec[0] * vec[0] + vec[1] * vec[1])

    @classmethod
    def prod_vec(cls, u, v) -> float:
        return u[0] * v[0] + u[1] * v[1]

    def calc_corner_angle(self) -> float:
        """ """
        u = [self.xc - self.x1, self.yc - self.y1]  #  vector C-A1
        v = [self.xc - self.x2, self.yc - self.y2]  #  vector C-A2

        cos_beta = GCodePatternDressUp.prod_vec(u, v) / (
            GCodePatternDressUp.norm_vec(u) * GCodePatternDressUp.norm_vec(v)
        )

        beta = acos(cos_beta)

        angle_str = "{:.3f}".format(RAD_TO_DEG(beta))
        half_angle_str = "{:.3f}".format(RAD_TO_DEG(beta * 0.5))

        print(f"corner angle = {angle_str} -> half = {half_angle_str}")

        return beta

    def calc_gap(self) -> float:
        """ """
        half_angle = self.corner_angle / 2.0

        gap = self.cutter_radius * (1 - sin(half_angle)) / sin(half_angle)

        print("gap          =", "{:.3f}".format(gap))

        return gap

    def calc_bisection_angles(self) -> Tuple[float, float]:
        """
        (a1x + b1y + c1 ) / k1 = +/- (a2x + b2y + c2 ) / k2

        The 2 angles are in [-PI/2 : +PI/2]
        """
        a1 = self.a1
        b1 = self.b1
        c1 = self.c1

        a2 = self.a2
        b2 = self.b2
        c2 = self.c2

        k1 = sqrt(a1 * a1 + b1 * b1)
        k2 = sqrt(a2 * a2 + b2 * b2)

        aa1 = a1 / k1 - a2 / k2
        bb1 = b1 / k1 - b2 / k2
        cc1 = c1 / k1 - c2 / k2

        aa2 = a1 / k1 + a2 / k2
        bb2 = b1 / k1 + b2 / k2
        cc2 = c1 / k1 + c2 / k2

        if bb1 == 0:
            slope_b1 = 99999999
            bisect1 = pi / 2.0
        else:
            slope_b1 = -aa1 / bb1
            bisect1 = atan(-aa1 / bb1)

        if bb2 == 0:
            slope_b2 = 99999999
            bisect2 = pi / 2.0
        else:
            slope_b2 = -aa2 / bb2
            bisect2 = atan(-aa2 / bb2)

        print("bisects angles:", RAD_TO_DEG(bisect1), " and ", RAD_TO_DEG(bisect2))

        # get the correct bisection with the correct orientation
        max_slope = max(abs(slope_b1), abs(slope_b2))
        coeff = min(0.1, 1.0 / max_slope)

        cc_dir_slope1_1 = [self.xc + coeff, self.yc + coeff * slope_b1]
        cc_dir_slope1_2 = [self.xc - coeff, self.yc - coeff * slope_b1]

        cc_dir_slope2_1 = [self.xc + coeff, self.yc + coeff * slope_b2]
        cc_dir_slope2_2 = [self.xc - coeff, self.yc - coeff * slope_b2]

        triangles = ((self.x1, self.y1), (self.xc, self.yc), (self.x2, self.y2))
        polygon = shapely.geometry.Polygon(triangles)

        pt1 = shapely.geometry.Point(cc_dir_slope1_1)
        pt2 = shapely.geometry.Point(cc_dir_slope1_2)
        pt3 = shapely.geometry.Point(cc_dir_slope2_1)
        pt4 = shapely.geometry.Point(cc_dir_slope2_2)

        if polygon.contains(pt1):
            bisect_ok = bisect1 + pi
            print("case 1: bisect 1 ok  : ", RAD_TO_DEG(bisect_ok))

        elif polygon.contains(pt2):
            bisect_ok = bisect1
            print("case 2: bisect 1 ok  : ", RAD_TO_DEG(bisect_ok))

        elif polygon.contains(pt3):
            bisect_ok = bisect2 + pi
            print("case 3: bisect 2 ok  : ", RAD_TO_DEG(bisect_ok))

        elif polygon.contains(pt4):
            bisect_ok = bisect2
            print("case 4: bisect 2 ok  : ", RAD_TO_DEG(bisect_ok))

        else:
            print("ZUT: failed to query the right bisection orientation!")
            bisect_ok = bisect1

        return bisect1, bisect2, bisect_ok

    def calc_dx_dy(self):
        return [self.gap * cos(self.bisect_ok), self.gap * sin(self.bisect_ok)]

    def make_dressup(self) -> str:
        """ """
        p_dx = "{:.3f}".format(self.dx)
        p_dy = "{:.3f}".format(self.dy)

        m_dx = "{:.3f}".format(-self.dx)
        m_dy = "{:.3f}".format(-self.dy)

        return f"""; ==================
; dressup start
G91
G1 X{p_dx}  Y{p_dy}
G1 X{m_dx}  Y{m_dy}
G90
; dressup end
; ==================


"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="gcode_dressup", description="add dogbones for gcode")

    # argument
    parser.add_argument("gcode", help="gcode to dressup")
    parser.add_argument("-r", "--cutter-radius", dest="cutter_radius", default=1.0, help="cutter radius")

    # version info
    parser.add_argument("--version", action="version", version="%s" % VERSION)

    options = parser.parse_args()

    cutter_radius = 1.0

    if True:
        v = [-0.0, 0.0, 0.0, 4.0, 4.0, 4.0]
        ff = GCodePatternDressUp(cutter_radius, v[0], v[1], v[2], v[3], v[4], v[5])
        res = ff.make_dressup()

        print(res)
