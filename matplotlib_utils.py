
import matplotlib.pyplot as plt
import numpy as np

import shapely.geometry


class MatplotLibUtils:
    '''
    Helper functions on Shapely
    '''
    MAPLOTLIB_DEBUG = False
    #MAPLOTLIB_DEBUG = True
    cnt = 1 # matplotlib figures

    @classmethod
    def MatplotlibDisplay(cls, title: str, geom: any, force: bool =False):
        '''
        '''
        if cls.MAPLOTLIB_DEBUG == False and force == False:
            return

        cls.cnt += 1

        # dispatch
        if geom.geom_type == 'LineString':
            cls._MatplotlibDisplayLineString(title, geom)
        if geom.geom_type == 'MultiLineString':
            cls._MatplotlibDisplayMultiLineString(title, geom)
        if geom.geom_type == 'Polygon':
            cls._MatplotlibDisplayPolygon(title, geom)
        if geom.geom_type == 'MultiPolygon':
            cls._MatplotlibDisplayMultiPolygon(title, geom)
        if geom.geom_type == 'GeometryCollection':
            cls._MatplotlibDisplayGeometryCollection(title, geom)
        else:
            pass

    @classmethod
    def rectify_y(cls, y) :
        yy = []
        for v in y:
            yy.append(-v)
        return np.array(yy)

    @classmethod
    def _MatplotlibDisplayLineString(cls, title: str, linestring: shapely.geometry.LineString):
        '''
        ''' 
        plt.figure(cls.cnt)
        plt.title(title)

        x = linestring.coords.xy[0]
        y = linestring.coords.xy[1]

        y = cls.rectify_y(y)

        # plot
        style = {
            0: 'bo-',
        }

        plt.axis('equal')
        plt.plot(x,y, style[0])
        plt.show()

    @classmethod
    def _MatplotlibDisplayMultiLineString(cls, title: str, multilinestring: shapely.geometry.MultiLineString):
        '''
        '''    
        plt.figure(cls.cnt)
        plt.title(title)

        style = {
            0: 'ro-',
            1: 'g+-',
            2: 'bo-',
            3: 'r+-',
            4: 'go-',
            5: 'b+-',
        }
        
        xx = []
        yy = []

        for line in multilinestring.geoms:
            ix = line.coords.xy[0]
            iy = line.coords.xy[1]

            iy = cls.rectify_y(iy)

            xx.append(ix)
            yy.append(iy)

        for k, (x,y) in enumerate(zip(xx,yy)):
            plt.plot(x, y, style[k%6])
      
        plt.axis('equal')
        plt.show()

    @classmethod
    def _MatplotlibDisplayPolygon(cls, title: str, polygon: shapely.geometry.Polygon):
        '''
        '''
        plt.figure(cls.cnt)
        plt.title(title)

        style_ext = {
            0: 'bo-'
        }
        style_int = {
            0: 'r+--',
            1: 'go-'
        }
        
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

        for k, (ix,iy) in enumerate(zip(interiors_xx,interiors_yy)):
            plt.plot(ix, iy, style_int[k%2])

        plt.axis('equal')
        plt.show()

    @classmethod
    def _MatplotlibDisplayMultiPolygon(cls, title: str, multipoly: shapely.geometry.MultiPolygon):
        '''
        '''
        plt.figure(cls.cnt)
        plt.title(title)

        style_ext = {
            0: 'bo-',
            1: 'ro-',
            2: 'go-',
        }
        style_int = {
            0: 'b+--',
            1: 'r+--',
            2: 'g+--'
        }

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
        for k, (x,y) in enumerate(zip(xx_ext,yy_ext)):
            plt.plot(x,y, style_ext[k%2])
        for k, (x,y) in enumerate(zip(xx_int,yy_int)):
            plt.plot(x,y,style_int[k%2])

        plt.axis('equal')
        plt.show()

    @classmethod
    def _MatplotlibDisplayGeometryCollection(cls, title: str, collection: shapely.geometry.GeometryCollection):
        '''
        '''
        plt.figure(cls.cnt)
        plt.title(title)

        style_ext = {
            0: 'ro-',
            1: 'go-',
            2: 'bo-'
        }
        style_int = {
            0: 'r+-',
            1: 'g+-',
            2: 'b+-'
        }

        pp = 0

        for geom in collection.geoms:

            if geom.geom_type == 'MultiPolygon':

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
                for x,y in zip(xx_ext,yy_ext):
                    pp += 1
                    plt.plot(x,y, style_ext[pp%3])
                for x,y in zip(xx_int,yy_int):
                    pp += 1
                    plt.plot(x,y,style_int[pp%3])

            if geom.geom_type == 'Polygon':
        
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

                for ix,iy in zip(interiors_xx,interiors_yy):
                    pp += 1
                    plt.plot(ix, iy, style_int[pp%3])

            if geom.geom_type == 'MultiLineString':

                xx = []
                yy = []

                for line in geom.geoms:
                    ix = line.coords.xy[0]
                    iy = line.coords.xy[1]

                    iy = cls.rectify_y(iy)

                    xx.append(ix)
                    yy.append(iy)

                for x,y in zip(xx,yy):
                    pp += 1
                    plt.plot(x, y, style_ext[pp%3])

            if geom.geom_type == 'LineString':

                x = geom.coords.xy[0]
                y = geom.coords.xy[1]

                y = cls.rectify_y(y)

                pp += 1

                plt.plot(x,y, style_ext[pp%3], color='black')

        plt.axis('equal')
        plt.show()

