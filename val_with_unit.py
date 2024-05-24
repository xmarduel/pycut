from typing import Any


class ValWithUnit(float):
    """
    A wrapper for float values with handy units conversion

    >>> x = ValWithUnit(22, "mm")
    >>> x
    >>> x.to_inch()
    >>> x.to_mm()
    >>> x.to_inch().to_fixed(5)

    Unfortunately, cannot modify x in place
    >>>  x.set_units("inch")
    so that the x value then changes together with its units.

    So do this
    >>> x = x.to_inch("inch")

    """

    def __new__(cls, value, units: str):
        instance = super().__new__(cls, value)
        instance.units = units
        return instance

    def __init__(self, value, units):
        # float.__init__(value)
        self.units = units

    # def __repr__(self):
    #    return "%4.*f %s" % (4, self, self.units)

    def to_inch(self):
        if self.units == "inch":
            return ValWithUnit(self, "inch")
        else:
            return ValWithUnit(self / 25.4, "inch")

    def to_mm(self):
        if self.units == "inch":
            return ValWithUnit(self * 25.4, "mm")
        else:
            return ValWithUnit(self, "mm")

    def to_fixed(self, level) -> str:
        """
        Format float value
        """
        return "%4.*f" % (level, self)

    def __mod__(self, units: Any):
        if units == "mm":
            return self.to_mm()
        else:
            return self.to_inch()

    def __imod__(self, units: Any):
        if self.units == units:
            return self
        else:
            if units == "mm":
                return self.to_mm()
            else:
                return self.to_inch()


if __name__ == "__main__":

    x = ValWithUnit(25.4, "mm")
    print("               x = ", x, id(x))
    x %= "inch"
    print('x %= "inch" => x = ', x, id(x))
