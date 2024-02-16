import matplotlib.pyplot as plt
import numpy as np
import math
from math import sqrt as sqrt

pi = np.pi


CUTTER_RADIUS = 3  # mm
OVERLAP = 0.66666666  # [0:1] in ratio -> cut size = (1 - overlap)
CUT_SIZE = CUTTER_RADIUS * (1 - OVERLAP)  # -> 1.0 mm
CUT_SIZE = 1.0
print("CUT_SIZE = ", CUT_SIZE)

POCKET_RADIUS = 10  # mm
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

POCKET_RADIUS_M_CUTTER = POCKET_RADIUS - CUTTER_RADIUS

PSEUDO_RADIUS = (
    POCKET_RADIUS_M_CUTTER * POCKET_RADIUS_M_CUTTER - CUTTER_RADIUS
)  # will be root-squared


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

        # list of radiuses : will be sqrt'ed
        z = np.linspace(0, PSEUDO_RADIUS, NB_POINTS)
        r = np.sqrt(z + CUTTER_RADIUS)  # -> max is POCKET_RADIUS_M_CUTTER

        print("z = ", z)
        print("r = ", r)

        # FIXME: at the beginning: too large!

        # when the radius of the spirale is increasing,
        # the delta(theta) must decrease for small increments in angle
        # (and radius) at every point
        t = np.sqrt(angles)

        x = r * np.sin(t)
        y = r * np.cos(t)

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
        N = math.floor(2 * pi * POCKET_RADIUS_M_CUTTER / SEGMENT_LEN)

        z2 = np.linspace(PSEUDO_RADIUS, PSEUDO_RADIUS, N)
        r2 = np.sqrt(z2 + CUTTER_RADIUS)
        t2 = t[-1] + np.linspace(0, 2 * pi, N)

        dx = r2 * np.sin(t2)
        dy = r2 * np.cos(t2)

        x = np.concatenate([x, dx])
        y = np.concatenate([y, dy])
        t = np.concatenate([t, t2])

        z = np.concatenate([z, z2])

        self.x = x
        self.y = y

    def plot(self):
        # ax = plt.figure().add_subplot(projection='3d')
        ax = plt.figure().add_subplot()

        ax.set_xlim([-10, 10])
        ax.set_ylim([-10, 10])
        ax.grid(True)
        ax.axis("equal")
        ax.plot(self.x, self.y, marker="o")

        plt.show()


class Square(Spiral):
    """
    x = ½ √( 2 + u² - v² + 2u√2 ) - ½ √( 2 + u² - v² - 2u√2 )
    y = ½ √( 2 - u² + v² + 2v√2 ) - ½ √( 2 - u² + v² - 2v√2 )
    """

    def __init__(self):
        super().__init__()

        super().make_arrays()

        self.xx = [Square.to_square_x(u, v) for (u, v) in zip(self.x, self.y)]
        self.yy = [Square.to_square_y(u, v) for (u, v) in zip(self.x, self.y)]

    def plot(self):
        ax = plt.figure().add_subplot()

        ax.set_xlim([-10, 10])
        ax.set_ylim([-10, 10])
        ax.grid(True)
        ax.axis("equal")
        ax.plot(self.xx, self.yy, marker="o")

        plt.show()

    @staticmethod
    def normalize(u, v):
        return [
            u / (POCKET_RADIUS - CUTTER_RADIUS),
            v / (POCKET_RADIUS - CUTTER_RADIUS),
        ]

    @staticmethod
    def to_square_x(u, v):
        u, v = Square.normalize(u, v)

        x = 0.5 * sqrt(2 + u * u - v * v + 2 * u * sqrt(2)) - 0.5 * sqrt(
            2 + u * u - v * v - 2 * u * sqrt(2)
        )

        return x * (POCKET_RADIUS - CUTTER_RADIUS)

    @staticmethod
    def to_square_y(u, v):
        u, v = Square.normalize(u, v)

        y = 0.5 * sqrt(2 - u * u + v * v + 2 * v * sqrt(2)) - 0.5 * sqrt(
            2 - u * u + v * v - 2 * v * sqrt(2)
        )

        return y * (POCKET_RADIUS - CUTTER_RADIUS)


if __name__ == "__main__":
    spiral = Spiral()
    spiral.plot()

    # square = Square()
    # square.plot()
