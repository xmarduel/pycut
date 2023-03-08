import svgpathtools
import math

pt1 = [335.4321, 69.71516199999999]
pt2 = [335.27971, 69.86756199999999]

ctrl = [335.33051, 69.816762]

def test1():
    st = (335.43211+69.71516199999999j)
    end = (335.27971+69.86756199999999j)
    ct = (335.33051+69.816762j)
    zz = svgpathtools.QuadraticBezier(st, ct, end)

    try:
        d1 = zz.length()
        print("test1:", d1)
    except :
        print("test1 exception")

def test2():
    st = (335.43211+69.715162j)
    ct = (335.33051+69.816762j)
    end = (335.27971+69.867562j)

    zz = svgpathtools.QuadraticBezier(st, ct, end)
  
    try:
        d1 = zz.length()
        print("test2:", d1)
    except :
        print("test2 exception")



if __name__ == '__main__':

    dx = pt1[0]-pt2[0]
    dy = pt1[1]-pt2[1]

    print("dist(pt1-pt2) = ", math.sqrt(dx*dx+dy*dy))

    test1()
    test2()












