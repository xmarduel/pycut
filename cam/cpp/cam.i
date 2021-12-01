%module cam
%{
/* Includes the header in the wrapper code */
#include "cam.h"
#include "FlexScan.h"
#include "offset.h"

extern "C" void hspocket(
    double** paths, int numPaths, int* pathSizes, double cutterDia,
    double**& resultPaths, int& resultNumPaths, int*& resultPathSizes);

extern "C" void vPocket(
    int debugArg0, int debugArg1,
    double** paths, int numPaths, int* pathSizes,
    double cutterAngle, double passDepth, double maxDepth,
    double**& resultPaths, int& resultNumPaths, int*& resultPathSizes);

extern "C" void separateTabs(
    double** pathPolygons, int numPaths, int* pathSizes,
    double** tabPolygons, int numTabPolygons, int* tabPolygonSizes,
    int& error,
    double**& resultPaths, int& resultNumPaths, int*& resultPathSizes);


%}
 
%include "typemaps.i"
%include "std_vector.i"

// the interface

void hspocket(
    double** paths, int numPaths, int* pathSizes, double cutterDia,
    double**& resultPaths, int& resultNumPaths, int*& resultPathSizes);

void vPocket(
    int debugArg0, int debugArg1,
    double** paths, int numPaths, int* pathSizes,
    double cutterAngle, double passDepth, double maxDepth,
    double**& resultPaths, int& resultNumPaths, int*& resultPathSizes);

void separateTabs(
    double** pathPolygons, int numPaths, int* pathSizes,
    double** tabPolygons, int numTabPolygons, int* tabPolygonSizes,
    int& error,
    double**& resultPaths, int& resultNumPaths, int*& resultPathSizes);



