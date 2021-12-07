
class ValWithUnit(float):
    '''
    A wrapper for float values with handy units conversion
    
    >>> x = ValWithUnit(22, "mm")
    >>> x
    >>> x.toInch()
    >>> x.fromInch()
    >>> x.toInch().toFixed(5)

    Unfortunately, cannot say
    >>>  x.set_units("inch")
    so that the x value then changes..
    
    '''
    def __new__(cls, value, units):
        x = float.__new__(cls, value)
        cls.units = units
        return x

    def __init__(self, value, units):
        self.value = value
        self.units = units
        
    def toInch(self):
        if self.units == "inch":
            return ValWithUnit(self, "inch")
        else:
            return ValWithUnit(self / 25.4, "mm")

    def fromInch(self):
        '''
        Convert x from inch to the current unit
        '''
        if self.units == "inch":
            return ValWithUnit(self, "inch")
        else:
            return ValWithUnit(self * 25.4, "mm")

    def set_units(self, units):
        '''
        BUGGY
        '''
        if units == self.units:
            pass
        else:
            self.units = units
            if units == "mm":
                self = self * 25.4
            else:
                self = self / 25.4

    def toFixed(self, level):
        '''
        Format float value
        '''
        return "%4.*f" % (level, self)



