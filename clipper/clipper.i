%module clipper
%{
/* Includes the header in the wrapper code */
#include "clipper.hpp"
%}
 
//%include "std_exception.i" 



/* Parse the header file to generate wrappers */
%include "clipper.hpp"

//%rename(__eq__)     IntPoint::operator==;
//%rename(IntPoint_eq) operator==(IntPoint, IntPoint);


%pythoncode %{

class ClipType:
    ctIntersection = 0
    ctUnion = 1
    ctDifference = 2
    ctXor =3

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

%}
