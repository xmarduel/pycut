
import ctypes
from typing import List
import time

from PySide6.QtGui import QVector3D
import numpy as np
 
NB = 1024 * 1024 * 2

def test_1():
    np_array = np.empty(3*NB, dtype=ctypes.c_float)
    k = 0
    while k < 3*NB:
        np_array[k] = k
        k += 1

    return np_array
    
def test_2():
    data : List[QVector3D] = []

    for k in range(NB):
        v = QVector3D()
        v.setX(3*k)
        v.setY(3*k+1)
        v.setZ(3*k+2)
        data.append(v)

    
    np_array = np.empty(3*len(data), dtype=ctypes.c_float)
    for k, vdata in enumerate(data):
        np_array[3*k+0] = vdata.x()
        np_array[3*k+1] = vdata.y()
        np_array[3*k+2] = vdata.z()

    return np_array



def main():
    t1 = time.time()
    v = test_1()
    t2 = time.time()

    DT1 = t2 -t1

    print("T1 = %f\n" % DT1)
    #print(v)
    
    t1 = time.time()
    v = test_2()
    t2 = time.time()

    DT2 = t2 -t1

    print("T2 = %f\n" % DT2)
    #print(v)


    print("ration = %f" % (DT2 / DT1))

  
if __name__ == '__main__':
    main()

