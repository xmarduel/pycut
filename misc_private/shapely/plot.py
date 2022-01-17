import matplotlib.pyplot as plt
from shapely.geometry import LineString, MultiPolygon, LinearRing, Point

a = Point(1,1).buffer(1)

x,y = a.exterior.coords.xy
plt.plot(x,y)
plt.show()