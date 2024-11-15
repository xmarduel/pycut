from typing import List
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt

import shapely.geometry  # type: ignore [import-untyped]


class MatplotLibUtils:
    """
    Plot Shapely objects
    """

    MAPLOTLIB_DEBUG = False
    # MAPLOTLIB_DEBUG = True

    cnt = 0  # matplotlib figures

    @classmethod
    def plot(cls, pts: npt.NDArray[np.complex128], title: str, style: str = "ro-"):
        """ """
        plt.figure(cls.cnt)
        plt.title(title + f" [{cls.cnt}]")

        xx = [pt.real for pt in pts]
        yy = [pt.imag for pt in pts]

        plt.plot(xx, yy, style)

        plt.axis("equal")
        plt.show()
        plt.pause(1)

    @classmethod
    def plot_geom(cls, title: str, geom: Any, force: bool = False) -> int:
        """ """
        return cls.display(title, geom, force)

    @classmethod
    def display(cls, title: str, geom: Any, force: bool = False) -> int:
        """ """
        # a counter
        cls.cnt += 1

        if cls.MAPLOTLIB_DEBUG == False and force == False:
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
    def rectify_y(cls, y):
        yy = []
        for v in y:
            yy.append(-v)
        return np.array(yy)

    @classmethod
    def _display_linestring(cls, title: str, linestring: shapely.geometry.LineString):
        """ """
        xs = linestring.coords.xy[0]
        ys = linestring.coords.xy[1]

        ys = cls.rectify_y(ys)

        _pts = [complex(x, y) for x, y in zip(xs, ys)]
        pts = np.array(_pts, dtype=np.complex128)

        cls.plot(pts, title, "bo-")

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

            iy = cls.rectify_y(iy)

            xx.append(ix)
            yy.append(iy)

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

        x = polygon.exterior.coords.xy[0]
        y = polygon.exterior.coords.xy[1]

        y = cls.rectify_y(y)

        plt.plot(x, y, style_ext[0])

        interiors_xx = []
        interiors_yy = []

        for interior in polygon.interiors:
            ix = interior.coords.xy[0]
            iy = interior.coords.xy[1]

            iy = cls.rectify_y(iy)

            interiors_xx.append(ix)
            interiors_yy.append(iy)

        for k, (ix, iy) in enumerate(zip(interiors_xx, interiors_yy)):
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

        for geom in multipoly.geoms:
            x = geom.exterior.coords.xy[0]
            y = geom.exterior.coords.xy[1]

            y = cls.rectify_y(y)

            xx_ext.append(x)
            yy_ext.append(y)

            for interior in geom.interiors:
                ix = interior.coords.xy[0]
                iy = interior.coords.xy[1]

                iy = cls.rectify_y(iy)

                xx_int.append(ix)
                yy_int.append(iy)

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
                xx_ext = []
                yy_ext = []

                xx_int = []
                yy_int = []

                for ch_geom in geom.geoms:
                    x = ch_geom.exterior.coords.xy[0]
                    y = ch_geom.exterior.coords.xy[1]

                    y = cls.rectify_y(y)

                    xx_ext.append(x)
                    yy_ext.append(y)

                    for interior in ch_geom.interiors:
                        ix = interior.coords.xy[0]
                        iy = interior.coords.xy[1]

                        iy = cls.rectify_y(iy)

                        xx_int.append(ix)
                        yy_int.append(iy)

                # plot
                for x, y in zip(xx_ext, yy_ext):
                    pp += 1
                    plt.plot(x, y, style_ext[pp % 3])
                for x, y in zip(xx_int, yy_int):
                    pp += 1
                    plt.plot(x, y, style_int[pp % 3])

            if geom.geom_type == "Polygon":
                x = geom.exterior.coords.xy[0]
                y = geom.exterior.coords.xy[1]

                y = cls.rectify_y(y)

                plt.plot(x, y, style_ext[0])

                interiors_xx = []
                interiors_yy = []

                for interior in geom.interiors:
                    ix = interior.coords.xy[0]
                    iy = interior.coords.xy[1]

                    iy = cls.rectify_y(iy)

                    interiors_xx.append(ix)
                    interiors_yy.append(iy)

                for ix, iy in zip(interiors_xx, interiors_yy):
                    pp += 1
                    plt.plot(ix, iy, style_int[pp % 3])

            if geom.geom_type == "MultiLineString":
                xx = []
                yy = []

                for line in geom.geoms:
                    ix = line.coords.xy[0]
                    iy = line.coords.xy[1]

                    iy = cls.rectify_y(iy)

                    xx.append(ix)
                    yy.append(iy)

                for x, y in zip(xx, yy):
                    pp += 1
                    plt.plot(x, y, style_ext[pp % 3])

            if geom.geom_type == "LineString":
                x = geom.coords.xy[0]
                y = geom.coords.xy[1]

                y = cls.rectify_y(y)

                pp += 1

                plt.plot(x, y, style_ext[pp % 3], color="black")

        plt.axis("equal")
        plt.show()
        plt.pause(1)
