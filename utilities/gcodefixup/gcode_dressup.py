VERSION = "0_1_0"

import argparse
from math import *
from typing import List, Tuple

import shapely.geometry
import shapely.ops


def RAD_TO_DEG(val):
    return val * 180.0 / pi


class Point:
    """ """

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def translate(self, u: "Point") -> "Point":
        """translate with a vector"""
        return Point(self.x + u.x, self.y + u.y)

    def transport(self, slope: float, coeff: float) -> "Point":
        """translate with a vector of dim (1, <slope>) scaled with <coeff>"""
        u = Point(1.0, slope).scale(coeff)
        return self.translate(u)

    def scale(self, coeff: float) -> "Point":
        """scale as a vector"""
        return Point(self.x * coeff, self.y * coeff)

    def norm(self) -> float:
        return sqrt(self.x * self.x + self.y * self.y)

    def coordinates(self) -> List[float]:
        return [self.x, self.y]


class GCodePatternDressUp:
    """ """

    def __init__(self, cutter_radius: float, pt1: Point, ptc: Point, pt2: Point):
        """
        From

        G1 X<x1> Y<y1>
        G1 X<ptc.x> Y<ptc.y>
        G1 X<x2> Y<y2>

        segment [pt1.x:C]:  a1.x + b1.y + c1 = 0
        segment [pt2.x:C]:  a2.x + b2.y + c2 = 0

        """
        self.cutter_radius = cutter_radius

        # the points
        self.pt1 = pt1
        self.ptc = ptc
        self.pt2 = pt2

        # slopes of the segments : y = mx + b  or ax + by + c = 0
        if ptc.x != pt1.x:
            self.a1 = (ptc.y - pt1.y) / (ptc.x - pt1.x)
            self.b1 = -1.0
            self.c1 = -(self.a1 * self.ptc.x + self.b1 * self.ptc.y)

        else:
            self.a1 = 1.0
            self.b1 = 0.0
            self.c1 = -(self.a1 * self.ptc.x + self.b1 * self.ptc.y)

        if pt2.x != ptc.x:
            self.a2 = (pt2.y - ptc.y) / (pt2.x - ptc.x)
            self.b2 = -1.0
            self.c2 = -(self.a2 * self.ptc.x + self.b2 * self.ptc.y)
        else:
            self.a2 = 1.0
            self.b2 = 0.0
            self.c2 = -(self.a2 * self.ptc.x + self.b2 * self.ptc.y)

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
        u = [self.ptc.x - self.pt1.x, self.ptc.y - self.pt1.y]  #  vector C-A1
        v = [self.ptc.x - self.pt2.x, self.ptc.y - self.pt2.y]  #  vector C-A2

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

        # the point on a given bisection in the given orientation (not too far!) is inside the triangle defined by the 3 points ?
        # then this bisection is the right one and the right orientation is this orientation + Pi (the opposite!)

        u = Point(self.ptc.x - self.pt1.x, self.ptc.y - self.pt1.y)  #  vector C-A1
        v = Point(self.ptc.x - self.pt2.x, self.ptc.y - self.pt2.y)  #  vector C-A2

        norm_u = u.norm()
        norm_v = v.norm()

        norm_min = min(norm_u, norm_v)

        norm_u_slope_1 = Point(1.0, slope_b1).norm()
        norm_u_slope_2 = Point(1.0, slope_b2).norm()

        norm_u_slope_max = max(norm_u_slope_1, norm_u_slope_2)

        coeff = 0.25 * norm_min / norm_u_slope_max
        # print("coeff [1]", coeff)

        pt_slope1_dir1 = self.ptc.transport(slope_b1, coeff)
        pt_slope1_dir2 = self.ptc.transport(slope_b1, -coeff)

        pt_slope2_dir1 = self.ptc.transport(slope_b2, coeff)
        pt_slope2_dir2 = self.ptc.transport(slope_b2, -coeff)

        polygon = shapely.geometry.Polygon(
            (
                shapely.geometry.Point(self.pt1.coordinates()),
                shapely.geometry.Point(self.ptc.coordinates()),
                shapely.geometry.Point(self.pt2.coordinates()),
            )
        )

        pt1 = shapely.geometry.Point(pt_slope1_dir1.coordinates())
        pt2 = shapely.geometry.Point(pt_slope1_dir2.coordinates())
        pt3 = shapely.geometry.Point(pt_slope2_dir1.coordinates())
        pt4 = shapely.geometry.Point(pt_slope2_dir2.coordinates())

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
    parser = argparse.ArgumentParser(
        prog="gcode_dressup", description="add dogbones for gcode"
    )

    # argument
    parser.add_argument("gcode", help="gcode to dressup")
    parser.add_argument(
        "-r", "--cutter-radius", dest="cutter_radius", default=1.0, help="cutter radius"
    )

    # version info
    parser.add_argument("--version", action="version", version="%s" % VERSION)

    options = parser.parse_args()

    cutter_radius = 1.0

    if True:
        pt1 = Point(0.0, 0.0)
        ptc = Point(0.0, 4.0)
        pt2 = Point(4.0, 4.0)

        ff = GCodePatternDressUp(cutter_radius, pt1, ptc, pt2)
        res = ff.make_dressup()

        print(res)
