import sys

import matplotlib.pyplot as plt
import numpy as np
import math
from math import sqrt as sqrt

pi = np.pi


CUTTER_RADIUS = 3  # mm
OVERLAP = 0.965  # [0:1] in ratio -> cut size = (1 - overlap)
CUT_SIZE = CUTTER_RADIUS * (1 - OVERLAP)  # -> 1.0 mm
# CUT_SIZE = 1.0
print("CUT_SIZE = ", CUT_SIZE)

POCKET_RADIUS = 15  # mm
NB_CIRCLES = math.floor((POCKET_RADIUS - CUTTER_RADIUS) / CUT_SIZE)
print("NB_CIRCLES = ", NB_CIRCLES)

SEGMENT_LEN = 1.0  # mm

# on each speudo circle of length 2pi*r there are
#  - 2pi*r           segments of lenght 1, or
#  - 2pi*r / len_seg segments of length len_seg
#
# Just sum them:
#    NB_POINTS = SUM n=1..NB_CIRCLES [2pi * R_n]
#    R_o = 0
#    R_n = R_n-1 + CUT_SIZE
#        = n*CUT_SIZE
#    => NB_POINTS = 2*pi SUM k=n..NB_CIRCLES [n*CUT_SIZE]
NB_CIRCLES_P_1 = NB_CIRCLES + 1

NB_POINTS = math.floor(
    (2 * pi / SEGMENT_LEN) * (CUT_SIZE * NB_CIRCLES * NB_CIRCLES_P_1 / 2)
)
print("NB_POINTS = ", NB_POINTS)

# NB_POINTS *= 2
# print("NB_POINTS = ", NB_POINTS)

POCKET_RADIUS_M_CUTTER = POCKET_RADIUS - CUTTER_RADIUS

POCKET_RADIUS_M_CUTTER_SQUARED = (
    POCKET_RADIUS_M_CUTTER * POCKET_RADIUS_M_CUTTER
)  # will be root-squared


PLUNGE_RATE = 32
CUT_RATE = 250
RAPID_RATE = 500


class Helix:
    """
    At (0,0) with a cutter of radius CUTTER_RADIUS, we perform a "full helix" from 0 to pass_depth.

    Every "full helix" makes circles around the origin at a radius R of CUTTER_RADIUS / 2 (noted "x"),
    each circle going down of 0.1 mm (FIXED)

              ///////b--R--x--o--x--R--b///////    b denoes the bordes of the cutted helix

    So the whole "hole" tobe cut will be of radius 1.5 * CUTTER_RADIUS

    To achieve an full helix going down  "H" mm [here 0.1 mm], feed rate and plunge rate are linkex

    Horizontal Travel : 2*PI*R   performed in D = f*T => Time = D / f = 2*Pi*R / feed
    Vertical Travel   : H        performed in H = p*T => Time = H / p = H / plunge_rate

    => plunge_rate = feed * H  / (2*PI*R)

    or , when the plunge rate is given, the helix periodic Height H will be

    => H = (2*PI*R) * plunge_rate / feed

    So if the feed is equal to the plunge rate, in 1 revolution, the cutter will plunge of 2PI*R, much too much

    Given feed and plunge rate, H is calculated. It should be around 0.1 mm

    Ex:
    - cutter diameter = 6 mm  => feed = 250  => plunge_rate = 1.3   so that H = 0.098  ... Ok
    - cutter diameter = 4 mm  => feed = 250  => plunge_rate = 2.0   so that H = 0.100  ... OK

    With the H calculated, we can define the full helix path, given that on the circle of radius R,
    each segment length is at most 0.1 mm : there need to be 2*PI*R / seg_len = points


    """

    def __init__(
        self, center, initial_depth=0.0, cut_depth=10.0, feed=250.0, plunge_rate=1.0
    ):
        """ """
        self.x = []
        self.y = []
        self.z = []

        HELIX_RADIUS = CUTTER_RADIUS / 2
        CIRCLE_TRAVEL = 2 * np.pi * HELIX_RADIUS
        SEG_LEN = 0.1

        HELIX_NB_POINTS = math.floor(CIRCLE_TRAVEL / SEG_LEN)

        self.revolution_height = CIRCLE_TRAVEL * plunge_rate / feed
        print("HELIX_PERIODIC_HEIGHT = ", self.revolution_height)

        self.nb_helixes = math.floor(cut_depth / self.revolution_height)
        self.revolution_height_last = (
            cut_depth - self.nb_helixes * self.revolution_height
        )

        pts = []

        for i in range(0, self.nb_helixes):
            for k in range(HELIX_NB_POINTS):
                x = center[0] + HELIX_RADIUS * math.cos(2 * np.pi * k / HELIX_NB_POINTS)
                y = center[1] + HELIX_RADIUS * math.sin(2 * np.pi * k / HELIX_NB_POINTS)
                z = (
                    -initial_depth
                    - i * self.revolution_height
                    - k * self.revolution_height / HELIX_NB_POINTS
                )

                pts.append([x, y, z])

        # and the last one
        for k in range(HELIX_NB_POINTS):
            x = center[0] + HELIX_RADIUS * math.cos(2 * np.pi * k / HELIX_NB_POINTS)
            y = center[1] + HELIX_RADIUS * math.sin(2 * np.pi * k / HELIX_NB_POINTS)
            z = (
                -initial_depth
                - self.nb_helixes * self.revolution_height
                - k * self.revolution_height_last / HELIX_NB_POINTS
            )

            pts.append([x, y, z])

        # and the last flat circle
        for k in range(HELIX_NB_POINTS):
            x = center[0] + HELIX_RADIUS * math.cos(2 * np.pi * k / HELIX_NB_POINTS)
            y = center[1] + HELIX_RADIUS * math.sin(2 * np.pi * k / HELIX_NB_POINTS)
            z = -initial_depth - cut_depth

            pts.append([x, y, z])

        self.pts = pts

    def plot(self):
        ax = plt.figure().add_subplot(projection="3d")
        # ax = plt.figure().add_subplot()

        x = [pt[0] for pt in self.pts]
        y = [pt[1] for pt in self.pts]
        z = [pt[2] for pt in self.pts]

        ax.plot(x, y, z, marker="o")
        # ax.axis("equal")
        ax.set_ylim([-4, 4])
        ax.set_xlim([-4, 4])
        # ax.grid(True)

        plt.show()


class Spiral:
    """ """

    def __init__(self):
        """ """
        self.x = None
        self.y = None

        self.make_arrays()

    def make_arrays(self):
        # Prepare arrays x, y

        # list of angles : will be sqrt'ed
        angles = np.linspace(
            0, (2 * pi * NB_CIRCLES) * (2 * pi * NB_CIRCLES), NB_POINTS
        )

        # when the radius of the spirale is increasing,
        # the delta(angles) must decrease for small increments in angle
        # at every point
        t = np.sqrt(angles)

        # list of radiuses : will be sqrt'ed
        z = np.linspace(0, POCKET_RADIUS_M_CUTTER_SQUARED, NB_POINTS)
        r = np.sqrt(z)  # -> max is POCKET_RADIUS_M_CUTTER

        # because the angles progression is of sqrt, so has to be the
        # progression of the radiuses!

        x = r * np.cos(t)
        y = r * np.sin(t)

        # last circle
        dt = t[-1] - t[-2]
        print(
            "dt =",
            dt,
            " => nb pts on circle/last spirale [est] = ",
            math.floor(2 * pi / dt),
            " => nb pts on circle",
            math.floor(2 * pi * POCKET_RADIUS_M_CUTTER / SEGMENT_LEN),
        )

        # discretized circle with N points
        N = math.floor(2 * pi / dt)
        # N = math.floor(2 * pi * POCKET_RADIUS_M_CUTTER / SEGMENT_LEN)

        N = N * 2

        r_circle = np.linspace(POCKET_RADIUS_M_CUTTER, POCKET_RADIUS_M_CUTTER, N)
        t_circle = t[-1] + np.linspace(0, 2 * pi, N)

        dx = r_circle * np.cos(t_circle)
        dy = r_circle * np.sin(t_circle)

        x = np.concatenate([x, dx])
        y = np.concatenate([y, dy])

        self.x = x
        self.y = y

    def plot(self):
        # ax = plt.figure().add_subplot(projection='3d')
        ax = plt.figure().add_subplot()

        ax.plot(self.x, self.y, marker="o")
        ax.axis("equal")
        ax.set_ylim([-20, 20])
        # ax.set_xlim([-10, 10])
        ax.grid(True)

        plt.show()

    def generate_g_code(self, ops):
        """ """
        clearance = 5.0
        x_shift_after_op = 11.5

        prolog = f"""
G21         ; Set units to mm
G90         ; Absolute positioning
G1 Z{clearance}  F{RAPID_RATE}      ; Move to clearance level

; Start the spindle
M3 S1000

;
; Tool Info
; Diameter:    6.0

"""

        epilog = f"""
; Retract
G1 Z{clearance} F{RAPID_RATE} 

; Stop the spindle
M5

; Return to 0,0
;G0 X0 Y0 F{RAPID_RATE} 

G0 Y0 F{RAPID_RATE}          ; move along Y axis
G0 X0 F{RAPID_RATE}          ; move along X axis

; Program End
M2
"""

        gcode = prolog

        for k, op in enumerate(ops):

            center = op["center"]
            cut_depth = op["cut_depth"]
            pass_depth = op["pass_depth"]

            nb_levels = math.floor(cut_depth / pass_depth) + 1

            levels = [0]
            for k in range(nb_levels):
                levels.append(-(k + 1) * pass_depth)
            levels[-1] = -cut_depth

            print("op levels:", levels)

            op_prolog = f""";
; Operation:    {k+1}
; Name:         pocket_spiral
; Type:         Pocket
; Paths:        1
; Direction:    Conventional
; Cut Depth:    {cut_depth}
; Pass Depth:   {pass_depth}
; Plunge rate:  {PLUNGE_RATE}
; Cut rate:     {CUT_RATE}
; Rapid rate:   {RAPID_RATE}
;
"""

            op_to_initial_position = f"""
; Path 1
; Rapid to initial position

;
;G1 X{center[0]} Y{center[1]} F{RAPID_RATE} 

G1 X{x_shift_after_op} F{RAPID_RATE}   ; move along X axis - in the middle
G1 Y{center[1]} F{RAPID_RATE}          ; move along Y axis
G1 X{center[0]} F{RAPID_RATE}          ; move along X axis

G1 Z0.0
"""

            op_epilog = f"""
; Retract
G1 Z{clearance} F{RAPID_RATE} 

; EXTRA: got right
G1 X{x_shift_after_op}
"""

            spirale_lines = []

            for k, level in enumerate(levels):

                if k == 0:
                    continue

                prev_level = levels[k - 1]

                helix = Helix(
                    center,
                    initial_depth=-prev_level,
                    cut_depth=prev_level - level,
                    feed=CUT_RATE,
                    plunge_rate=PLUNGE_RATE,
                )

                spirale_lines.append(
                    f"; Helix REVOLUTION HEIGHT      : {helix.revolution_height}"
                )
                spirale_lines.append(f"; - initial depth : {-prev_level} ")
                spirale_lines.append(f"; - cut depth     : {prev_level - level} ")

                for i, pt in enumerate(helix.pts):
                    xx = "%4.*f" % (4, pt[0])
                    yy = "%4.*f" % (4, pt[1])
                    zz = "%4.*f" % (4, pt[2])

                    if i == 0:
                        spirale_lines.append(f"G1 X{xx} Y{yy} Z{zz} F{PLUNGE_RATE}")
                    else:
                        spirale_lines.append(f"G1 X{xx} Y{yy} Z{zz}")

                spirale_lines.append("; Spiral ")

                spirale_lines.append(f"G1 Z{level} F{CUT_RATE}")

                for x, y in zip(self.x, self.y):
                    xx = "%4.*f" % (4, x + center[0])
                    yy = "%4.*f" % (4, y + center[1])

                    spirale_lines.append(f"G1 X{xx} Y{yy}")

                spirale_lines.append(f"G1 Z{prev_level}")

                spirale_lines.append(f"G1 X{center[0]} Y{center[1]}")

                spirale = "\n".join(spirale_lines)

            gcode += op_prolog + op_to_initial_position + spirale + op_epilog

        gcode += epilog

        fp = open("gcode.nc", "w")
        fp.write(gcode)
        fp.close()


class Square(Spiral):

    def __init__(self):
        super().__init__()

        super().make_arrays()

        self.xx = [Square.to_square_x(u, v) for (u, v) in zip(self.x, self.y)]
        self.yy = [Square.to_square_y(u, v) for (u, v) in zip(self.x, self.y)]

    def plot(self):
        ax = plt.figure().add_subplot()

        ax.plot(self.xx, self.yy, marker="o")
        ax.axis("equal")
        ax.set_ylim([-20, 20])
        # ax.set_xlim([-10, 10])
        ax.grid(True)

        plt.show()

    @staticmethod
    def normalize(u, v):
        return [
            u / POCKET_RADIUS_M_CUTTER,
            v / POCKET_RADIUS_M_CUTTER,
        ]

    @staticmethod
    def to_square_x(u, v):
        """
        x = ½ √( 2 + u² - v² + 2u√2 ) - ½ √( 2 + u² - v² - 2u√2 )
        y = ½ √( 2 - u² + v² + 2v√2 ) - ½ √( 2 - u² + v² - 2v√2 )
        """
        u, v = Square.normalize(u, v)

        uu = u * u
        vv = v * v

        a = 2 + uu - vv + 2 * u * sqrt(2)
        b = 2 + uu - vv - 2 * u * sqrt(2)

        a = a if a > 0.0 else 0.0
        b = b if b > 0.0 else 0.0

        x = 0.5 * sqrt(a) - 0.5 * sqrt(b)

        return x * POCKET_RADIUS_M_CUTTER

    @staticmethod
    def to_square_y(u, v):
        u, v = Square.normalize(u, v)

        uu = u * u
        vv = v * v

        a = 2 - uu + vv + 2 * v * sqrt(2)
        b = 2 - uu + vv - 2 * v * sqrt(2)

        a = a if a > 0.0 else 0.0
        b = b if b > 0.0 else 0.0

        y = 0.5 * sqrt(a) - 0.5 * sqrt(b)

        return y * POCKET_RADIUS_M_CUTTER


if __name__ == "__main__":

    # helix = Helix([0, 0], initial_depth=0, cut_depth=10, feed=250.0, plunge_rate=32.0)
    # helix.plot()

    # sys.exit()

    spiral = Spiral()
    # spiral.plot()

    ops = [
        {"center": [0.0, 0.0], "cut_depth": 25.0, "pass_depth": 10.0},
        {"center": [0.0, 170.0], "cut_depth": 25.0, "pass_depth": 10.0},
        #    {"center": [0.0, 85.0], "cut_depth": 17.0, "pass_depth": 10.0},
    ]

    spiral.generate_g_code(ops)

    # square = Square()
    # square.plot()
