from typing import List
from typing import Any
from typing import cast

import numpy as np
import numpy.typing as npt

import matplotlib.pyplot as plt

import shapely.geometry


class ShapelyMatplotlib:
    """
    Plot Shapely objects
    """

    #MAPLOTLIB_DEBUG = False
    MAPLOTLIB_DEBUG = True

    COEFF_Y = -1.0 # for svg

    cnt = 0  # matplotlib figures counter

    @classmethod
    def plot_geom(cls, title: str, geom: Any,) -> int:
        """ """
        return cls.display(title, geom)

    @classmethod
    def display(cls, title: str, geom: Any, figure=True) -> int:
        """ """
        # a counter
        #cls.cnt += 1

        if cls.MAPLOTLIB_DEBUG == False:
            return cls.cnt

        # dispatch
        if geom.geom_type == "LineString":
            cls._display_linestring(title, geom, figure)
        if geom.geom_type == "LinearRing":
            cls._display_linestring(title, geom, figure)
        if geom.geom_type == "MultiLineString":
            cls._display_multilinestring(title, geom, figure)
        if geom.geom_type == "Polygon":
            cls._display_polygon(title, geom, figure)
        if geom.geom_type == "MultiPolygon":
            cls._display_multipolygon(title, geom, figure)
        if geom.geom_type == "GeometryCollection":
            cls._display_geometrycollection(title, geom, figure)
        else:
            pass

        return cls.cnt

    @classmethod
    def linestring_np_coords(cls, linestring: shapely.geometry.LineString | shapely.geometry.LinearRing):
        """ """
        np_coords = np.array(linestring.coords)
    
        npxs = np_coords[:, 0]
        npys = np_coords[:, 1] * cls.COEFF_Y
    
        return npxs, npys

    @classmethod
    def _display_linestring(cls, title: str, linestring: shapely.geometry.LineString | shapely.geometry.LinearRing, figure=True, pause=True):
        """ """
        if figure:
            plt.figure(cls.cnt)
            
        plt.title(title + f" [{cls.cnt}]")

        npx, npy = cls.linestring_np_coords(linestring)
        
        plt.plot(npx, npy, "bo-")
        plt.axis("equal")
        plt.show()
        
        if pause:
            plt.pause(1)
            #plt.close()

    @classmethod
    def _display_multilinestring(cls, title: str, multilinestring: shapely.geometry.MultiLineString, figure=True, pause=True):
        """ """
        if figure:
            plt.figure(cls.cnt)
            
        plt.title(title + f" [{cls.cnt}]")

        style = {
            0: "ro-",
            1: "g+-",
            2: "bo-",
            3: "r+-",
            4: "go-",
            5: "b+-",
        }

        for k, linestring in enumerate(multilinestring.geoms):
            npx, npy = cls.linestring_np_coords(linestring)

            plt.plot(npx, npy, style[k % 6])

        plt.axis("equal")
        plt.show()

        if pause:
            plt.pause(1)
            #plt.close()

    @classmethod
    def _display_polygon(cls, title: str, polygon: shapely.geometry.Polygon, figure=True, pause=True):
        """ """
        if figure:
            plt.figure(cls.cnt)

        plt.title(title + f" [{cls.cnt}]")

        style_ext = {0: "bo-"}
        style_int = {0: "r+--", 1: "go-"}

        npx, npy = cls.linestring_np_coords(polygon.exterior)
        plt.plot(npx, npy, style_ext[0])

        for k, interior in enumerate(polygon.interiors):
            npx, npy = cls.linestring_np_coords(interior)
            plt.plot(npx, npy, style_int[k % 2])

        plt.axis("equal")
        plt.show()

        if pause:
            plt.pause(1)
            #plt.close()

    @classmethod
    def _display_multipolygon(cls, title: str, multipoly: shapely.geometry.MultiPolygon, figure=True, pause=True):
        """ """
        if figure:
            plt.figure(cls.cnt)
            
        plt.title(title + f" [{cls.cnt}]")

        style_ext = {
            0: "bo-",
            1: "ro-",
            2: "go-",
        }
        style_int = {
            0: "b+--",
            1: "r+--", 
            2: "g+--"
        }

        for k, poly in enumerate(multipoly.geoms):
            npx, npy = cls.linestring_np_coords(poly.exterior)
            plt.plot(npx, npy, style_ext[k % 3])

            for q, interior in enumerate(poly.interiors):
                npx, npy = cls.linestring_np_coords(interior)
                plt.plot(npx, npy, style_int[q % 3])

        plt.axis("equal")
        plt.show()

        if pause:
            plt.pause(1)
            #plt.close()

    @classmethod
    def _display_geometrycollection(cls, title: str, collection: shapely.geometry.GeometryCollection, figure=True, pause=True):
        """ """
        plt.figure(cls.cnt)
        plt.title(title + f" [{cls.cnt}]")

        for geom in collection.geoms:
            if geom.geom_type == "MultiPolygon":
                geom = cast(shapely.geometry.MultiPolygon, geom)
                cls._display_multipolygon(title, geom, figure=False, pause=False)

            if geom.geom_type == "Polygon":
                geom = cast(shapely.geometry.Polygon, geom)
                cls._display_polygon(title, geom, figure=False, pause=False)

            if geom.geom_type == "MultiLineString":
                geom = cast(shapely.geometry.MultiLineString, geom)
                cls._display_multilinestring(title, geom, figure=False, pause=False)

            if  geom.geom_type =="LineString" or geom.geom_type == "LinearRing":
                geom = cast(shapely.geometry.LineString, geom)
                cls._display_linestring(title, geom, figure=False, pause=False)

        plt.axis("equal")
        plt.show()

        if pause:
            plt.pause(1)
            #plt.close()
