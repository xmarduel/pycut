import sys

import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon, LinearRing
import shapely

class Poly2Svg:
    '''
    '''
    def __init__(self, poly: Polygon):
        self.poly = poly

    def to_svg_str(self):
        '''
        '''
        svg = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg version="1.1"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg">
  <g>
   %(path)s
  </g>
</svg>'''

        return svg % { 'path': self.poly.svg(scale_factor=0.1)}

    def write_file(self, filename: str):
        '''
        '''
        fp = open(filename, 'w')
        fp.write(self.to_svg_str())
        fp.close()

        print("wrote file : %s" % filename)



# create a shapely polygon with no holes 
# create a shapely polygon with 1 hole 

poly_ext = [(10,10), (20,10), (20,20), (10,20)]
poly_int =  [(12,12), (18,12), (18,18), (12,18)]

linearring = LinearRing(poly_ext)

poly1 = Polygon(linearring)
poly2 = Polygon(linearring, holes=[poly_int])

poly1 = shapely.geometry.polygon.orient(poly1)
poly2 = shapely.geometry.polygon.orient(poly2)

h1 = Poly2Svg(poly1)
h2 = Poly2Svg(poly2)

h1.write_file('poly1.svg')
h2.write_file('poly2.svg')

