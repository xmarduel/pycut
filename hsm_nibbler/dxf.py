"""
Helper methods for converting .dxf source files into shapely Polygons.
Used by the test implementation main.py.
"""

from typing import List, Tuple

from math import *

from ezdxf.entities.lwpolyline import LWPolyline as DxfPolyline
from ezdxf.query import EntityQuery as DxfPolylines
from shapely.geometry import LineString, MultiLineString, Point, Polygon, LinearRing, MultiPoint, MultiPolygon  # type: ignore

CIRCLE_RES = 500

# Introduce coordinate jitter by clamping coordinates to this number of decimal places.
# Used for testing.
# Set to "0" to disable.
DP = 0

def round_points(points):
    """ Used in testing. Clamps points to rounded coordinates. """
    if not DP:
        return points
    return [(round(point[0], DP), round(point[1], DP)) for point in points]

def weighted(p1, p2, alpha):
    return p1[0] + (p2[0] - p1[0]) * alpha, p1[1] + (p2[1] - p1[1]) * alpha

def circle(x, y, r, n=None, sa=0, ea=2*pi):
    if n is None:
        n = pi * r * GeometrySettings.RESOLUTION
    n *= abs((ea - sa) / (2 * pi))
    n = ceil(n)
    res = []
    for i in range(n + 1):
        a = sa + i * (ea - sa) / n
        newpt = (x + r * cos(a), y + r * sin(a))
        if not res or newpt != res[-1]:
            res.append(newpt)
    return res

def circle_to_linestring(circle) -> LineString:
    radius = getattr(circle.dxf, "radius")
    center = getattr(circle.dxf, "center")
    return Point(center).buffer(radius).simplify(0.1).boundary

def polyline_to_linestring(entity) -> LineString:
    points: List[Tuple[float, float]] = []
    lastx, lasty = entity[-1][0:2]
    lastbulge = entity[-1][4]
    for point in entity:
        x, y = point[0:2]
        if lastbulge:
            theta = 4 * atan(lastbulge)
            dx, dy = x - lastx, y - lasty
            mx, my = weighted((lastx, lasty), (x, y), 0.5)
            angle = atan2(dy, dx)
            dist = sqrt(dx * dx + dy * dy)
            d = dist / 2
            r = abs(d / sin(theta / 2))
            c = d / tan(theta / 2)
            cx = mx - c * sin(angle)
            cy = my + c * cos(angle)
            sa = atan2(lasty - cy, lastx - cx)
            ea = sa + theta
            points += round_points(circle(cx, cy, r, CIRCLE_RES, sa, ea))
            points.append((x, y))
        else:
            points.append((x, y))
        lastbulge = point[4]
        lastx, lasty = x, y
    return LineString(points)

def dxf_to_polygon(modelspace) -> MultiPolygon:
    """ Convert .dxf polyline into shapely Polygon. """
    rings = []
    for entity in modelspace:
        if entity.dxftype() == "CIRCLE":
            rings.append(circle_to_linestring(entity))
        elif entity.dxftype() == "LWPOLYLINE":
            rings.append(polyline_to_linestring(entity))
        else:
            print(f"Unsupported dxf entity: {entity.dxftype()}")

    parents = []
    for ring in rings:
        coveres = []
        covered_by = False
        for parent_index, parent in enumerate(parents):
            if Polygon(ring).covers(parent):
                coveres.append(parent_index)
            if Polygon(parent).covers(ring):
                covered_by = True
        for not_parent in sorted(coveres, reverse=True):
            parents.pop(not_parent)
        if not covered_by:
            parents.append(ring)

    polygons = []
    for parent in parents:
        holes = []
        for ring in rings:
            if ring is parent:
                continue
            if Polygon(parent).covers(ring):
                holes.append(ring)
        polygon = Polygon(parent, holes=holes)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)
        polygons.append(polygon)

    return MultiPolygon(polygons)
