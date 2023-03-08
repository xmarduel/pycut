import sys

import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon, LinearRing
import shapely

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
middle of a face -> not a corner and setup as first oint of the 
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
print("initial linestring", ls1)
print("initial linestring", ls2)
print("-----------------------------------------------------------")

lr1 = LinearRing(coords1)
lr2 = LinearRing(coords2)
print("-------- as linear ring, there is an orientation")
print("initial linearring", lr1, 'is_ccw', lr1.is_ccw)
print("initial linearring", lr2, 'is_ccw', lr2.is_ccw)
print("-----------------------------------------------------------")

p1 = Polygon(lr1)  # we could take l1
p2 = Polygon(lr2)  # we could take l2


print("")
print("----- resulting polygons --------")
print("poly p1 : orientation", p1, "area=", p1.area, p1.exterior, p1.exterior.is_ccw)
print("poly p2 : orientation", p2, "area=", p2.area, p2.exterior, p2.exterior.is_ccw)
print("-----------------------------------------------------------")

# TRICK: properly orient the polygons -> the 2 poly have the same orientation , but which one ?
p1 = shapely.geometry.polygon.orient(p1)
p2 = shapely.geometry.polygon.orient(p2)

print("")
print("----- after re-orienting the polygons")
print("oriented poly p1 : orientation", p1, "area=", p1.area, p1.exterior, p1.exterior.is_ccw)
print("oriented poly p2 : orientation", p2, "area=", p2.area, p2.exterior, p2.exterior.is_ccw)
print(".... notice how the polygons have the same orientation... ccw")
# --------------------- LINEAR RING

ls_1 = LineString(p1.exterior.coords)
lr_1 = p1.exterior

print("")

off_ls1_left = ls_1.parallel_offset(1, 'left', resolution=4)
off_lr1_left = lr_1.parallel_offset(1, 'left', resolution=4)

off_ls1_right = ls_1.parallel_offset(1, 'right', resolution=4)
off_lr1_right = lr_1.parallel_offset(1, 'right', resolution=4)

# ------------------------------------------

print("----- we offset on the left the the linestring/linearring: result is 'left' -> 'inside' as it is ccw")

print("off1_left", off_ls1_left)
print("off2_left", off_lr1_left)

print("off1_right", off_ls1_right)
print("off2_right", off_lr1_right)

x1s_L,y1s_L = off_ls1_left.coords.xy
x2s_L,y2s_L = off_lr1_left.coords.xy

x1s_R,y1s_R = off_ls1_right.coords.xy
x2s_R,y2s_R = off_lr1_right.coords.xy

plt.title("left / right offsets")
plt.plot(x1s_L,y1s_L, 'bo-', label="ls L")
plt.plot(x2s_L,y2s_L, 'r+--', label="lr L")
plt.plot(x1s_R,y1s_R, 'bo-', label="ls R")
plt.plot(x2s_R,y2s_R, 'r+--', label="lr R")
plt.legend()
plt.show()


# -------------------------------------------------------
# AND THE RESULTING ORIENTATIONS:  ** CHANGED iN SHAPELY 2.0 **
# -------------------------------------------------------
ls_o_left = LinearRing(off_ls1_left)
ls_o_right = LinearRing(off_ls1_right)

print("orientation of offset : left is-ccw ->", ls_o_left.is_ccw)
print("orientation of offset : right is-ccw ->", ls_o_right.is_ccw)


# -------------------------------------------------------
# -------------------------------------------------------
# TRICK: add a point in the middle of a segment
#     so that the start point is NOT a corner 
# -------------------------------------------------------
# -------------------------------------------------------

x0 = coords1[0][0]
y0 = coords1[0][1]

x1 = coords1[1][0]
y1 = coords1[1][1]

new_pt = ((x0+x1)/2, (y0+y1)/2)
coords1 = [new_pt] + coords1[1:] + [coords1[0]] 


ls1 = LineString(coords1)
lr1 = LinearRing(coords1)

print("initial linestring", ls1)
print("initial linearring", lr1)

p1 = Polygon(ls1)
p2 = Polygon(lr1)

# properly orient the polygon
p1 = shapely.geometry.polygon.orient(p1)
p2 = shapely.geometry.polygon.orient(p2)

print("oriented (ccw) poly p1", p1, p1.exterior.is_ccw)
print("oriented (ccw) poly p2", p2, p2.exterior.is_ccw)

# --------------------- LINEAR RING

ls_1 = LineString(p1.exterior)
lr_1 = p1.exterior

print("linestring ls_1", ls_1)
print("linearring lr_1", lr_1)

off_ls1_left = ls_1.parallel_offset(1, 'left', resolution=4)
off_lr1_left = lr_1.parallel_offset(1, 'left', resolution=4)

off_ls1_right = ls_1.parallel_offset(1, 'right', resolution=4)
off_lr1_right = lr_1.parallel_offset(1, 'right', resolution=4)

# ------------------------------------------

print("off1_left", off_ls1_left)
print("off2_left", off_lr1_left)

print("off1_right", off_ls1_right)
print("off2_right", off_lr1_right)

x1s_L,y1s_L = off_ls1_left.coords.xy
x2s_L,y2s_L = off_lr1_left.coords.xy

x1s_R,y1s_R = off_ls1_right.coords.xy
x2s_R,y2s_R = off_lr1_right.coords.xy

plt.title("left / right offsets")
plt.plot(x1s_L,y1s_L, 'bo-', label="ls")
plt.plot(x2s_L,y2s_L, 'r+--', label="lr")
plt.plot(x1s_R,y1s_R, 'bo-', label="ls right")
plt.plot(x2s_R,y2s_R, 'r+--', label="lr right")
plt.legend()
plt.show()

# --------------------------------------------------------------
# AND THE REUSLTING ORIENTATIONS:  ** CHANGED iN SHAPELY 2.0 **
# --------------------------------------------------------------
ls_o_left = LinearRing(off_ls1_left)
ls_o_right = LinearRing(off_ls1_right)

print("orientation of offset : left is-ccw ->", ls_o_left.is_ccw)
print("orientation of offset : right is-ccw ->", ls_o_right.is_ccw)


