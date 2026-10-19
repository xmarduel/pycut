from typing import List
from typing import Any
from typing import cast

import numpy as np
import numpy.typing as npt

import matplotlib.pyplot as plt

import shapely.geometry


class MatplotLibUtils:
    """
    Plot Shapely objects
    """

    #MAPLOTLIB_DEBUG = False
    MAPLOTLIB_DEBUG = True

    cnt = 0  # matplotlib figures counter

    @classmethod
    def plot_geom(cls, title: str, geom: Any) -> int:
        """ """
        return cls.display(title, geom)

    @classmethod
    def display(cls, title: str, geom: Any) -> int:
        """ """
        # a counter
        cls.cnt += 1

        if cls.MAPLOTLIB_DEBUG == False:
            return cls.cnt

        # dispatch
        if geom.geom_type == "LineString":
            cls._display_linestring(title, geom)
        if geom.geom_type == "LinearRing":
            cls._display_linestring(title, geom)
        if geom.geom_type == "MultiLineString":
            cls._display_multilinestring(title, geom)
        if geom.geom_type == "Polygon":
            cls._display_polygon(title, geom)
        if geom.geom_type == "MultiPolygon":
            cls._display_multipolygon(title, geom)
        if geom.geom_type == "GeometryCollection":
            cls._display_geometrycollection(title, geom)
        else:
            pass

        return cls.cnt
    
    @classmethod
    def _display_linestring(cls, title: str, linestring: shapely.geometry.LineString):
        """ """
        xs = linestring.coords.xy[0]
        ys = linestring.coords.xy[1]

        npxs = np.array(xs, dtype=np.float64)
        npys = np.array(ys, dtype=np.float64) * -1.0

        plt.figure(cls.cnt)
        plt.title(title + f" [{cls.cnt}]")

        plt.plot(npxs, npys, "bo-")

        plt.axis("equal")
        plt.show()
        plt.pause(1)

    @classmethod
    def _display_multilinestring(
        cls, title: str, multilinestring: shapely.geometry.MultiLineString
    ):
        """ """
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

        xx = []
        yy = []

        for line in multilinestring.geoms:
            ix = line.coords.xy[0]
            iy = line.coords.xy[1]

            npix = np.array(ix, dtype=np.float64)
            npiy = np.array(iy, dtype=np.float64) * -1.0

            xx.append(npix)
            yy.append(npiy)

        for k, (x, y) in enumerate(zip(xx, yy)):
            plt.plot(x, y, style[k % 6])

        plt.axis("equal")
        plt.show()
        plt.pause(1)

    @classmethod
    def _display_polygon(cls, title: str, polygon: shapely.geometry.Polygon):
        """ """
        plt.figure(cls.cnt)
        plt.title(title + f" [{cls.cnt}]")

        style_ext = {0: "bo-"}
        style_int = {0: "r+--", 1: "go-"}

        ring = polygon.exterior
        
        xs = ring.coords.xy[0]
        ys = ring.coords.xy[1]

        npxs = np.array(xs, dtype=np.float64)
        npys = np.array(ys, dtype=np.float64) * -1.0

        plt.plot(npxs, npys, style_ext[0])

        interiors_xx = []
        interiors_yy = []

        for interior in polygon.interiors:
            ix = interior.coords.xy[0]
            iy = interior.coords.xy[1]

            npix = np.array(ix, dtype=np.float64)
            npiy = np.array(iy, dtype=np.float64) * -1.0

            interiors_xx.append(npix)
            interiors_yy.append(npiy)

        for k, (npix, npiy) in enumerate(zip(interiors_xx, interiors_yy)):
            plt.plot(ix, iy, style_int[k % 2])

        plt.axis("equal")
        plt.show()
        plt.pause(1)

    @classmethod
    def _display_multipolygon(
        cls, title: str, multipoly: shapely.geometry.MultiPolygon
    ):
        """ """
        plt.figure(cls.cnt)
        plt.title(title + f" [{cls.cnt}]")

        style_ext = {
            0: "bo-",
            1: "ro-",
            2: "go-",
        }
        style_int = {0: "b+--", 1: "r+--", 2: "g+--"}

        xx_ext = []
        yy_ext = []

        xx_int = []
        yy_int = []

        for poly in multipoly.geoms:
            xs = poly.exterior.coords.xy[0]
            ys = poly.exterior.coords.xy[1]

            npxs = np.array(xs, dtype=np.float64)
            npys = np.array(ys, dtype=np.float64) * -1.0

            xx_ext.append(npxs)
            yy_ext.append(npys)

            for interior in poly.interiors:
                ix = interior.coords.xy[0]
                iy = interior.coords.xy[1]

                npix = np.array(ix, dtype=np.float64)
                npiy = np.array(iy, dtype=np.float64) * -1.0

                xx_int.append(npix)
                yy_int.append(npiy)

        # plot
        for k, (x, y) in enumerate(zip(xx_ext, yy_ext)):
            plt.plot(x, y, style_ext[k % 2])
        for k, (x, y) in enumerate(zip(xx_int, yy_int)):
            plt.plot(x, y, style_int[k % 2])

        plt.axis("equal")
        plt.show()
        plt.pause(1)

    @classmethod
    def _display_geometrycollection(
        cls, title: str, collection: shapely.geometry.GeometryCollection
    ):
        """ """
        plt.figure(cls.cnt)
        plt.title(title + f" [{cls.cnt}]")

        style_ext = {0: "ro-", 1: "go-", 2: "bo-"}
        style_int = {0: "r+-", 1: "g+-", 2: "b+-"}

        pp = 0

        for geom in collection.geoms:
            if geom.geom_type == "MultiPolygon":
                geom = cast(shapely.geometry.MultiPolygon, geom)


                xx_ext = []
                yy_ext = []

                xx_int = []
                yy_int = []

                for ch_geom in geom.geoms:
                    xs = ch_geom.exterior.coords.xy[0]
                    ys = ch_geom.exterior.coords.xy[1]

                    npxs = np.array(xs, dtype=np.float64)
                    npys = np.array(ys, dtype=np.float64) * -1.0
                
                    xx_ext.append(npxs)
                    yy_ext.append(npys)

                    for interior in ch_geom.interiors:
                        ix = interior.coords.xy[0]
                        iy = interior.coords.xy[1]

                        npix = np.array(ix, dtype=np.float64)
                        npiy = np.array(iy, dtype=np.float64) * -1.0

                        xx_int.append(npix)
                        yy_int.append(npiy)

                # plot
                for x, y in zip(xx_ext, yy_ext):
                    pp += 1
                    plt.plot(x, y, style_ext[pp % 3])
                for x, y in zip(xx_int, yy_int):
                    pp += 1
                    plt.plot(x, y, style_int[pp % 3])

            if geom.geom_type == "Polygon":
                geom = cast(shapely.geometry.Polygon, geom)

                xs = geom.exterior.coords.xy[0]
                ys = geom.exterior.coords.xy[1]

                npxs = np.array(xs, dtype=np.float64)
                npys = np.array(ys, dtype=np.float64) * -1.0

                plt.plot(npxs, npys, style_ext[0])

                interiors_xx = []
                interiors_yy = []

                for interior in geom.interiors:
                    ix = interior.coords.xy[0]
                    iy = interior.coords.xy[1]

                    npix = np.array(ix, dtype=np.float64)
                    npiy = np.array(iy, dtype=np.float64) * -1.0

                    interiors_xx.append(npix)
                    interiors_yy.append(npiy)

                for npix, npiy in zip(interiors_xx, interiors_yy):
                    pp += 1
                    plt.plot(npix, npiy, style_int[pp % 3])

            if geom.geom_type == "MultiLineString":
                geom = cast(shapely.geometry.MultiLineString, geom)

                xx = []
                yy = []

                for line in geom.geoms:
                    ix = line.coords.xy[0]
                    iy = line.coords.xy[1]

                    npix = np.array(ix, dtype=np.float64)
                    npiy = np.array(iy, dtype=np.float64) * -1.0

                    xx.append(npix)
                    yy.append(npiy)

                for x, y in zip(xx, yy):
                    pp += 1
                    plt.plot(x, y, style_ext[pp % 3])

            if geom.geom_type == "LineString":
                xs = geom.coords.xy[0]
                ys = geom.coords.xy[1]

                npxs = np.array(xs, dtype=np.float64)
                npys = np.array(ys, dtype=np.float64) * -1.0

                pp += 1

                plt.plot(npxs, npys, style_ext[pp % 3], color="black")

        plt.axis("equal")
        plt.show()
        plt.pause(1)
