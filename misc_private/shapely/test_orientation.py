import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon, LinearRing, MultiLineString
import shapely

from shapely_matplotlib import ShapelyMatplotlib as shapely_plt

import numpy as np

'''
DOC:
----

orienting a polygon: p1 = shapely.geometry.polygon.orient(p1, sign=1.0)
-------------------------------------------------------------
Returns a properly oriented copy of the given polygon. 
The signed area of the result will have the given sign. 
A sign of 1.0 means that the coordinates of the product’s exterior ring will be 
oriented counter-clockwise and the interior rings (holes) will be oriented clockwise.

Left and right are determined by following the direction of the 
given geometric points of the LineString.
'''

'''
This show how the outside offset of a quadra is somehow buggy when
the coords list is setup with the 4 corners coordinate

To fix the offset, we use a new additional point that is in the 
middle of a face -> not a corner and setup as first point of the 
coordinate list.

=> then the outside offset is perfect!

'''

print("")
print("")
print("")
print("")
print("")
print("")

# -------- SETUP INITIAL LINESTRING/LINEARRINF AND POLYGONS ---------------

# we give two list of coords with "opposite directions"
 
coords1 = [(10,10), (20,10), (20,20), (10,20)]
coords2 = [(10,10), (10,20), (20,20), (20,10)]

ls1 = LineString(coords1)
ls2 = LineString(coords2)

print("----- these two linestrings do not have the same orientation")
print(f"initial linestring ls1 {ls1}")
print(f"initial linestring ls2 {ls2}")
print("-----------------------------------------------------------")

lr1 = LinearRing(coords1)
lr2 = LinearRing(coords2)
print("-------- linear rings have an orientation -----------------")
print(f"initial linearring lr1 {lr1} is_ccw ? {lr1.is_ccw}")
print(f"initial linearring lr2 {lr2} is_ccw'? {lr2.is_ccw}")
print("-----------------------------------------------------------")

p1 = Polygon(lr1)  # we could take ls1
p2 = Polygon(lr2)  # we could take ls2

print("")
print("----- resulting polygons --------")
print(f"poly p1(lr1) : {p1}    area={p1.area}  exterior {p1.exterior} exterior ccw ? {p1.exterior.is_ccw}")
print(f"poly p2(lr2) : {p2}    area={p2.area}, exterior {p2.exterior} exterior cc2 ? {p2.exterior.is_ccw}")
print("-----------------------------------------------------------")

# TRICK: properly orient the polygons -> the 2 poly have the same orientation , but which one ?
op1 = shapely.geometry.polygon.orient(p1)
op2 = shapely.geometry.polygon.orient(p2)

print("")
print("----- after re-orienting the polygons")
print(f"oriented poly op1 : {op1}  area={op1.area} exterior {op1.exterior} exterior ccw ? {op1.exterior.is_ccw}")
print(f"oriented poly op2 : {op2}  area={op2.area} exterior {op2.exterior} exterior ccw ? {op2.exterior.is_ccw}")
print(".... notice how the polygons have the same orientation... ccw")
# --------------------- LINEAR RING

print("")

print(f"op1.exterior is {op1.exterior}")

print("")

off_ext_L = op1.exterior.parallel_offset(1, 'left', resolution=4)
off_ext_R = op1.exterior.parallel_offset(1, 'right', resolution=4)

# ------------------------------------------

print("----- we offset on the left the linearring (the poly exterior): result is 'left' -> 'inside' as it is ccw")

print(f"off_ext_L {off_ext_L}")
print(f"off_ext_R {off_ext_R}")

shapely_plt.COEFF_Y = 1.0

offsets = MultiLineString([op1.exterior, off_ext_L, off_ext_R])
shapely_plt.display("left / right offsets of linearrings", offsets)

# -------------------------------------------------------------
# AND THE RESULTING ORIENTATIONS:  ** CHANGED iN SHAPELY 2.0 **
# -------------------------------------------------------------

lr_o_L = LinearRing(off_ext_L)
lr_o_R = LinearRing(off_ext_R)

print("orientation of lr offset : left  is-ccw ->", lr_o_L.is_ccw)
print("orientation of lr offset : right is-ccw ->", lr_o_R.is_ccw)

# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------
# TRICK: add a point in the middle of a segment so that the start point is NOT a corner 
# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------

print("")
print("")
print("  ---------- with point in the middle of a segment -------------- ")
print("")
print("")

x0 = coords1[0][0]
y0 = coords1[0][1]

x1 = coords1[1][0]
y1 = coords1[1][1]

new_pt = ((x0+x1)/2, (y0+y1)/2)
coords1 = [new_pt] + coords1[1:] + [coords1[0]] 

lr = LinearRing(coords1)

print(f"initial linear ring {lr}")

poly = Polygon(lr)
# orient the polygon
opoly = shapely.geometry.polygon.orient(poly)

print(f"oriented opol {opoly} : {opoly.exterior} ccw = {opoly.exterior.is_ccw}")

# --------------------- LINEAR RING

print("opoly.exterior ", opoly.exterior)

off_lr_L = opoly.exterior.parallel_offset(1, 'left', resolution=4)
off_lr_R = opoly.exterior.parallel_offset(1, 'right', resolution=4)

# ------------------------------------------

offsets = MultiLineString([opoly.exterior, off_lr_L, off_lr_R])
shapely_plt.display("left / right offsets of linearrings (Improved)", offsets, figure=False)

# --------------------------------------------------------------
# AND THE REUSLTING ORIENTATIONS:  ** CHANGED iN SHAPELY 2.0 **
# --------------------------------------------------------------

print(f"orientation of offset L: ccw = {LinearRing(off_lr_L.coords).is_ccw}")
print(f"orientation of offset R: ccw = {LinearRing(off_lr_R.coords).is_ccw}")


