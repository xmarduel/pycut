%module clipper_613
%{
/* Includes the header in the wrapper code */
#include "clipper.hpp"
%}
 
%include "typemaps.i"
%include "std_vector.i"


/* Parse the header file to generate wrappers */
%include "clipper.hpp"

namespace std
{
  %template(IntPointVector) vector<ClipperLib::IntPoint>;
  %template(PathVector) vector<ClipperLib::Path>;
  %template(PolyNodes) vector<ClipperLib::PolyNode>;
}


%extend std::vector<ClipperLib::IntPoint>{
    void reverse() {
        std::reverse((*self).begin(), (*self).end());
    }
}


%pythoncode %{

# miserable attempt to debug - simply add python code like this
def IntPointVector__repr__(self):
    res = "IntPointVector #%d\n" % len(self)
    for i, pt in enumerate(self):
       res += "  [%d] %8d %8d\n" % (i, pt.X, pt.Y)
    return res 
IntPointVector.__repr__ = IntPointVector__repr__


def PathVector__repr__(self):
    res = "PathVector #%d\n" % len(self)
    for k, path in enumerate(self):
        #res += repr(path)
        for i, pt in enumerate(path):
            res += "  [%d] %8d %8d\n" % (i, pt.X, pt.Y)
    return res 
PathVector.__repr__ = PathVector__repr__


class ClipType:
    ctIntersection = 0
    ctUnion = 1
    ctDifference = 2
    ctXor = 3

class PolyType:
    ptSubject = 0
    ptClip = 1

class PolyFillType:
    pftEvenOdd = 0
    pftNonZero = 1
    pftPositive = 2
    pftNegative = 3

class InitOptions:
    ioReverseSolution = 1
    ioStrictlySimple = 2
    ioPreserveCollinear = 4

class JoinType:
    jtSquare = 0 
    jtRound = 1 
    jtMiter= 2

class EndType:
    etClosedPolygon = 0
    etClosedLine = 1
    etOpenButt = 2
    etOpenSquare = 3
    etOpenRound = 4

class EdgeSide:
    esLeft = 1
    esRight = 2

def dumpIntPoint(label, pt):
    if label: print(label)
    print(pt.X, pt.Y)

def dumpPath(label, path):
    if label: print("---- path  ", label , "  len#", len(path))
    for pt in path:
        dumpIntPoint(None, pt)

def dumpPaths(label, paths):
    print(label)
    for path in paths:
        print("---- path   len#", len(path))
        dumpPath(None, path)

%}



