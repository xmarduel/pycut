import sys

import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon, LinearRing
import shapely

'''
This show how the outside offset of a quadra is somehow buggy when
the coords list is setup with the 4 corners coordinate

To fix the offset, we use a new additional point that is in the 
middle of a face -> not a corner and setup as first oint of the 
coordinate list.

=> then the outside offset is perfect!

'''

# ------------- SETUP INITIAL LINESTRING AND POLYGONS --------------------

# we give two list of coords with "opposite directions"
 
coords1 = [(10,10), (20,10), (20,20), (10,20)]
coords2 = [(10,10), (10,20), (20,20), (20,10)]

l1 = LineString(coords1)
l2 = LineString(coords2)

print("----- these two linestrings do not have the same orientation")
print("initial linestring", l1)
print("initial linestring", l2)
print("-----------------------------------------------------------")

p1 = Polygon(l1)
p2 = Polygon(l2)


print("")
print("----- resulting polygons")
print("poly p1 : check yourself the orientation", p1)
print("poly p2 : check yourself the orientation", p2)
print("-----------------------------------------------------------")

# TRICK: properly orient the polygons -> the 2 poly have the same orientation , but which one ?
p1 = shapely.geometry.polygon.orient(p1)
p2 = shapely.geometry.polygon.orient(p2)

print("")
print("----- after re-orienting the polygons")
print("oriented poly p1 : check yourself the orientation", p1)
print("oriented poly p2 : check yourself the orientation", p2)
print(".... notice how the polygons have the same orientation... (but which one ?!!!)")
# --------------------- LINEAR RING

ls1 = LineString(p1.exterior.coords)
ls2 = LineString(p2.exterior.coords)

print("")
print("----- resulting linestrings")
print("linestring ls1", ls1)
print("linestring ls2", ls2)


off1_left = ls1.parallel_offset(1, 'left')
off2_left = ls2.parallel_offset(1, 'left')

off1_right = ls1.parallel_offset(1, 'right')
off2_right = ls2.parallel_offset(1, 'right')

# ------------------------------------------

print("----- we offset on the left the two lines: is'nt it strange ? result is 'left' -> 'inside' as it should be, so infact the DISPLAY of the list of coords is wrong!")
print("off1_left", off1_left)
print("off2_left", off2_left)

x1,y1 = off1_left.coords.xy
x2,y2 = off2_left.coords.xy
plt.title("left offset")
plt.plot(x1,y1, 'bo-')
plt.plot(x2,y2, 'r+-')
plt.show()

# ------------------------------------------

print("----- we offset on the right the two lines: is'nt it strange ? result is 'right' -> 'outside' as it should be, so infact the DISPLAY of the list of coords is wrong!")
print("off1_right", off1_right)
print("off2_right", off2_right)

x1,y1 = off1_right.coords.xy
x2,y2 = off2_right.coords.xy
plt.title("right offset")
plt.plot(x1,y1, 'bo-')
plt.plot(x2,y2, 'r+--')
plt.show()

# ------------------------------------------
# --------------------- LINEAR RING
# ------------------------------------------

# LINEAR RING DOES NOT HELP!

'''
# poly to linear ring
lr1 = LinearRing(p1.exterior.coords)
lr2 = LinearRing(p2.exterior.coords)

print("linearring lr1", lr1)
print("linearring lr2", lr2)

off1_left = lr1.parallel_offset(1, 'left')
off2_left = lr2.parallel_offset(1, 'left')

off1_right = lr1.parallel_offset(1, 'right')
off2_right = lr2.parallel_offset(1, 'right')

# ------------------------------------------

print("off1_left", off1_left)
print("off2_left", off2_left)

x1,y1 = off1_left.coords.xy
x2,y2 = off2_left.coords.xy
plt.plot(x1,y1, 'bo-')
plt.plot(x2,y2, 'r+--')
plt.show()

# ------------------------------------------

print("off1_right", off1_right)
print("off2_right", off2_right)

x1,y1 = off1_right.coords.xy
x2,y2 = off2_right.coords.xy
plt.plot(x1,y1, 'bo-')
plt.plot(x2,y2, 'r+--')
plt.show()

'''

# -------------------------------------------------------
# TRICK: add a point in the middle of a segment
#  so that the start point is NOT a corner 
# -------------------------------------------------------
x0 = coords1[0][0]
y0 = coords1[0][1]

x1 = coords1[1][0]
y1 = coords1[1][1]

new_pt = ((x0+x1)/2, (y0+y1)/2)
coords1 = [new_pt] + coords1[1:] + [coords1[0]] 

x0 = coords2[0][0]
y0 = coords2[0][1]

x1 = coords2[1][0]
y1 = coords2[1][1]

new_pt = ((x0+x1)/2, (y0+y1)/2)
coords2 = [new_pt] + coords2[1:] + [coords2[0]] 


l1f = LineString(coords1)
l2f = LineString(coords2)

print("initial linestring", l1f)
print("initial linestring", l2f)

p1f = Polygon(l1f)
p2f = Polygon(l2f)

# TRICK: properly orient the polygons -> the 2 poly have the same orientation 
p1f = shapely.geometry.polygon.orient(p1f)
p2f = shapely.geometry.polygon.orient(p2f)

print("oriented (ccw) poly p1f", p1f)
print("oriented (ccw) poly p2f", p2f)

# --------------------- LINEAR RING

ls1f = LineString(p1f.exterior.coords)
ls2f = LineString(p2f.exterior.coords)

print("linestring ls1f", ls1f)
print("linestring ls2f", ls2f)

off1_left = ls1.parallel_offset(1, 'left')
off2_left = ls2.parallel_offset(1, 'left')

off1_right = ls1f.parallel_offset(1, 'right')
off2_right = ls2f.parallel_offset(1, 'right')

# ------------------------------------------

print("off1_left", off1_left)
print("off2_left", off2_left)

x1,y1 = off1_left.coords.xy
x2,y2 = off2_left.coords.xy
plt.title("left offset")
plt.plot(x1,y1, 'bo-')
plt.plot(x2,y2, 'r+--')
plt.show()

# ------------------------------------------

print("off1_right", off1_right)
print("off2_right", off2_right)

x1,y1 = off1_right.coords.xy
x2,y2 = off2_right.coords.xy
plt.title("right offset")
plt.plot(x1,y1, 'bo-')
plt.plot(x2,y2, 'r+--')
plt.show()

