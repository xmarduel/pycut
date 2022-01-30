import sys

import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon, LinearRing
import shapely

# ------------- SETUP INITIAL LINSTEING AND POLYGONS

# we give two list of coords wit "oppsite directions
 
coords1 = [(10,10), (20,10), (20,20), (10,20)]
coords2 = [(10,10), (10,20), (20,20), (20,10)]

hole = [(11,11), (19,11), (19,19), (11,19), (11,11)]

l1 = LineString(coords1)
l2 = LineString(coords2)

print("initial linestring", l1)
print("initial linestring", l2)

p1 = Polygon(l1)
p2 = Polygon(l2)

# TRICK: properly orient the polygons -> the 2 poly have the same orientation 
p1 = shapely.geometry.polygon.orient(p1)
p2 = shapely.geometry.polygon.orient(p2)

svg = p1.svg()
print(svg)

ph = Polygon(coords1, holes=[hole])

svg = ph.svg()
print(svg)

sys.exit()

print("oriented (ccw) poly p1", p1)
print("oriented (ccw) poly p2", p2)

# --------------------- LINEAR RING

ls1 = LineString(p1.exterior.coords)
ls2 = LineString(p2.exterior.coords)

print("linestring ls1", ls1)
print("linestring ls2", ls2)

off1_left = ls1.parallel_offset(1, 'left')
off2_left = ls2.parallel_offset(1, 'left')

off1_right = ls1.parallel_offset(1, 'right')
off2_right = ls2.parallel_offset(1, 'right')

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

# ------------------------------------------
# --------------------- LINEAR RING
# ------------------------------------------

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

# -------------------------------------------------------
# TRICK: add a point in thr middle of a segment
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

