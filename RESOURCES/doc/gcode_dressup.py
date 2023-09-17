class GCodeDressUp:
    """
    """
    def __init__(self, x0: float, y0: float, xc: float, yc: float, x1: float, y1: float):
        """
        From 

        G1 X<xo> Y<yo>
        G1 X<xc> Y<yc>
        G1 X<x1> Y<y1>

        """
        self.xo = x0
        self.yo = y0
        self.xc = xc
        self.yc = yc
        self.x1 = x1
        self.y1 = y1

        # slopes of the segments
        self.mo = (yc-y0) / (xc - x0)
        self.m1 = (y1-yc) / (x1 - xc)

        # incoming stock lines def
        self.k0 = self.calc_k0() # TODO
        self.k1 = self.calc_k1() # TODO

        self.dx , self.dy = self.calc_dx_dy() # TODO

    def calc_k0(self)-> float:
        """
        """
        return 0.0 # TODO
    
    def calc_k1(self)-> float:
        """
        """
        return 0.0 # TODO

    def calc_gap(self) -> float:
        """
        """
        return 0.0  # TODO
    
    def calc_bisection_angle(self) -> float:
        """
        """
        return 0.0
    
    def calc_dx_dy(self) :
        """
        """
        return (0.0, 0.0)  # TODO
    
    def make_dressup(self) -> str :
        """
        """
        return """; dressup start
        G91
        G1 X{self.dx}  Y{self.dy}
        G1 X-{self.dx} Y-{self.dy}
        G90
        ; dressup end
        """