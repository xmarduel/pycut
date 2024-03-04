#!/usr/bin/env python3
"""
Debugging functions.

Recognises the following environment variables:
    HSM_DEBUG: Set to enable any debug output. Default = not set.
    HSM_DEBUG_RES: (Optional) Resolution of output image in dpi. Default = 1000 dpi.
    HSM_DEBUG_FILENAME: (Optional) Specify output image filename. Default = /tmp/hsm.png
    HSM_DEBUG_SCREEN: (Optional) Attempt to output image to screen. Default = not set.
"""

import os

from typing import List, Optional, Union, Any

try:
    import matplotlib.pyplot as plt    # type: ignore
except ImportError:
    pass

from shapely.geometry import MultiPolygon, Polygon  # type: ignore

from hsm_nibble.voronoi_centers import VoronoiCenters  # type: ignore

class Display:
    """
    Use matplotlib.pyplot to display outline of polygons and voronoi diagram.
    """
    filename: str = "/tmp/hsm.png"
    resolution: int = 1000
    screen: bool = False
    initialised: bool = False
    count: int = 0
    colours: List[str] = ["blue", "orange", "green", "cyan", "magenta", "purple", "brown", "grey", "olive", "pink", "yellow"]

    def __init__(self):
        if not os.environ.get("HSM_DEBUG"):
            return

        if not plt:
            print("Error: matplotlib.pyplot not imported.")
            return

        if os.environ.get("HSM_DEBUG_RES"):
            self.resolution = int(os.environ.get("HSM_DEBUG_RES"))

        if os.environ.get("HSM_DEBUG_FILENAME"):
            self.filename = os.environ.get("HSM_DEBUG_FILENAME")

        if os.environ.get("HSM_DEBUG_SCREEN"):
            self.screen = True

        print(f"Writing debug image: {self.filename} at resolution: {self.resolution} dpi")

        plt.gca().set_aspect('equal')

        self.initialised = True

    def display(self,
            polygons: Optional[List[Union[Polygon, MultiPolygon]]] = None,
            voronoi: Optional[VoronoiCenters] = None,
            path: Optional[List] = None) -> None:
        if not self.initialised:
            return

        self.count += 1
        if self.count != 1:
            return
        print(self.count)

        if polygons is None:
            polygons = []

        for index, key in enumerate(polygons.keys()):
            multi = polygons[key]
            colour = self.colours[index % len(self.colours)]
            print(f"  {key}: {colour}")
            if multi.type != "MultiPolygon":
                multi = MultiPolygon([multi])
            for polygon in multi.geoms:
                for ring in [polygon.exterior] + list(polygon.interiors):
                    x, y = ring.xy
                    plt.plot(x, y, c=colour, linewidth=0.01)

        if voronoi:
            for edge in voronoi.edges.values():
                x = []
                y = []
                for point in edge.coords:
                    x.append(point[0])
                    y.append(point[1])
                plt.plot(x, y, c="red", linewidth=0.1)
                plt.plot(x[0], y[0], 'o', c='red', markersize=0.1)
                plt.plot(x[-1], y[-1], 'o', c='red', markersize=0.1)

        if path:
            for entity in path:
                x = []
                y = []
                for point in entity.path.coords:
                    x.append(point[0])
                    y.append(point[1])
                style = "solid"
                colour = "black"
                if type(entity).__name__ == "Line":
                    if str(entity.move_style) == "MoveStyle.RAPID_OUTSIDE":
                        colour = "purple"
                        style = "dotted"
                    if str(entity.move_style) == "MoveStyle.RAPID_INSIDE":
                        colour = "red"
                plt.plot(x, y, c=colour, linestyle=style, linewidth=0.01)

        if self.filename:
            plt.savefig(self.filename, dpi=self.resolution, bbox_inches='tight')
        if self.screen:
            plt.show()

        print("Done writing debug image section.")
