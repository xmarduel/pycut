
class ValWithUnit(float):
    '''
    A wrapper for float values with handy units conversion
    
    >>> x = ValWithUnit(22, "mm")
    >>> x
    >>> x.to_inch()
    >>> x.toMm()
    >>> x.to_inch().toFixed(5)

    Unfortunately, cannot say
    >>>  x.set_units("inch")
    so that the x value then changes..

    So do this
    >>> x = x.to_inch("inch")
    
    '''
    def __new__(cls, value, units):
        x = float.__new__(cls, value)
        return x

    def __init__(self, value, units):
        self.value = value
        self.units = units
        
    def to_inch(self):
        if self.units == "inch":
            return ValWithUnit(self, "inch")
        else:
            return ValWithUnit(self / 25.4, "inch")

    def toMm(self):
        if self.units == "inch":
            return ValWithUnit(self * 25.4, "mm")
        else:
            return ValWithUnit(self, "mm")

    def toFixed(self, level):
        '''
        Format float value
        '''
        return "%4.*f" % (level, self)



