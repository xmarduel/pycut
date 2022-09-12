import sys

import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon, LinearRing
import shapely

def poly_2_svg(poly: Polygon):
    svg = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg version="1.1"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg">
  <g>
   %(path)s
  </g>
</svg>'''

    return svg % { 'path': poly.svg(scale_factor=0.1)}

def write_file(filename: str, data: str):
    '''
    '''
    fp = open(filename, 'w')
    fp.write(data)
    fp.close()

    print("wrote file : %s" % filename)



# create a shapely polygon with no holes 
# create a shapely polygon with 1 hole 

poly_ext = [(10,10), (20,10), (20,20), (10,20)]
poly_int =  [(12,12), (18,12), (18,18), (12,18)]

line = LineString(poly_ext)

poly1 = Polygon(line)
poly2 = Polygon(line, holes=[poly_int])

poly1 = shapely.geometry.polygon.orient(poly1)
poly2 = shapely.geometry.polygon.orient(poly2)

svg1 = poly_2_svg(poly1)
svg2 = poly_2_svg(poly2)

write_file('poly1.svg', svg1)
write_file('poly2.svg', svg2)

