

import matplotlib.pyplot as plt

import shapely
from shapely.geometry import LineString, Polygon, LinearRing, MultiPolygon
from shapely.ops import unary_union
'''


'''

print("")
print("")
print("")
print("")
print("")
print("")

# -------- SETUP INITIAL LINESTRING/LINEARRINF AND POLYGONS ---------------

# we give two list of coords with "opposite directions"
 
coords1 = [(0,0), (2,0), (2,2), (0,2)]
coords2 = [(4,0), (6,0), (6,2), (4,2)]
coords3 = [(5,0), (7,0), (7,2), (6,2)]
coords4 = [(8,0), (9,0), (9,2), (8,2)]

p1 = Polygon(coords1)
p2 = Polygon(coords2) 
p3 = Polygon(coords3)
p4 = Polygon(coords4)


res = unary_union([p1,p2,p3, p4])
print(res)


plt.title("unary_union")
for poly in res.geoms:
    if poly.geom_type == 'Polygon':
        xx, yy = poly.exterior.coords.xy
        plt.plot(xx,yy, 'bo-', label="poly")
plt.legend()
plt.show()

# ---------------------------------------------------------

# we give two list of coords with "opposite directions"
 
coords1 = [(0,0), (2,0), (2,2), (0,2)]
coords2 = [(4,0), (6,0), (6,2), (4,2)]
coords3 = [(1,1), (5,1), (5,3), (1,3)]

p1 = Polygon(coords1)
p2 = Polygon(coords2) 
p3 = Polygon(coords3)

p1p2 = MultiPolygon([p1, p2])
p1p3 = MultiPolygon([p1, p3])
p2p3 = MultiPolygon([p2, p3])

print("p1p2 valid ?", p1p2.is_valid)
print("p1p3 valid ?", p1p3.is_valid)
print("p2p3 valid ?", p2p3.is_valid)

p2up3 = p2.union(p3)

print("p2up3 valid ?", p2up3.is_valid)

res = unary_union([p1,p2,p3])
print(res)

if res.geom_type == 'Polygon':
    plt.title("unary_union")
    xx, yy = res.exterior.coords.xy
    plt.plot(xx,yy, 'bo-', label="poly")
    plt.legend()
    plt.show()