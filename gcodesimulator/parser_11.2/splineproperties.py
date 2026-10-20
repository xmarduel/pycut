# This file is a part of "pycut" application.

# This file was originally ported from "splineproperties.cpp" class
# of "Candle" application written by Hayrullin Denis Ravilevich
# (https://github.com/Denvi/Candle)

# Copyright 2020-2030 Xavier Marduel

from enum import Enum


class SplineProperties:
    """ """
    class SplineType(Enum):
        CUBIC_SPLINE = 0
        QUADRATIC_SPLINE = 1

    def __init__(self):
        self.type = SplineProperties.SplineType.CUBIC_SPLINE
        self.controlPoint1 = None
        self.controlPoint2 = None  # None for quadratic
