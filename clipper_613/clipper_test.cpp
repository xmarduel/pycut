#include "clipper.hpp"
	
	//from clipper.hpp ...
	//typedef signed long long cInt;
	//struct IntPoint {cInt X; cInt Y;};
	//typedef std::vector<IntPoint> Path;
	//typedef std::vector<Path> Paths;
#include <iostream>

using namespace ClipperLib;
	
int test_combine() {
    Paths subj(2), clip(1), solution;
	
	//define outer blue 'subject' polygon
	subj[0] << 
	  IntPoint(180,200) << IntPoint(260,200) <<
	  IntPoint(260,150) << IntPoint(180,150);
	
	//define subject's inner triangular 'hole' (with reverse orientation)
	subj[1] << 
	  IntPoint(215,160) << IntPoint(230,190) << IntPoint(200,190);
	
	//define orange 'clipping' polygon
	clip[0] << 
	  IntPoint(190,210) << IntPoint(240,210) << 
	  IntPoint(240,130) << IntPoint(190,130);
	
	//draw input polygons with user-defined routine ... 
	//DrawPolygons(subj, 0x160000FF, 0x600000FF); //blue
	//DrawPolygons(clip, 0x20FFFF00, 0x30FF0000); //orange
	
	//perform intersection ...
	Clipper c;
	c.AddPaths(subj, ptSubject, true);
	c.AddPaths(clip, ptClip, true);
	c.Execute(ctIntersection, solution, pftNonZero, pftNonZero);

	//draw solution with user-defined routine ... 
	//DrawPolygons(solution, 0x3000FF00, 0xFF006600); //solution shaded green

    std::cout << "Execute Paths combine " << std::endl;
	std::cout << solution;

    return 0;
}

int test_open_paths_combine() {
	Path contour;
    contour.push_back(IntPoint(100,100));
    contour.push_back(IntPoint(600,100));
   
    Paths tabs;
	
	Path tab1;
	tab1.push_back(IntPoint(200,80));
    tab1.push_back(IntPoint(250,80));
	tab1.push_back(IntPoint(250,120));
    tab1.push_back(IntPoint(200,120));
	//tab1.push_back(IntPoint(200,80));

	Path tab2;
	tab2.push_back(IntPoint(400,80));
    tab2.push_back(IntPoint(450,80));
	tab2.push_back(IntPoint(450,120));
    tab2.push_back(IntPoint(400,120));
	//tab2.push_back(IntPoint(400,80));

	tabs.push_back(tab1);
	tabs.push_back(tab2);

    Clipper c;
    c.AddPath(contour, ptSubject, false); // "open"
	c.AddPaths(tabs, ptClip, true); // "close"

    // --------------------- ctIntersection
	PolyTree polytree1;

    bool rc1 = c.Execute(ctIntersection, 
            polytree1,
            pftNonZero, 
            pftNonZero);

    std::cout << "Execute polytree intersection result: " << rc1 << std::endl;
	std::cout << polytree1.Total() << std::endl;
    Paths paths;
	OpenPathsFromPolyTree(polytree1, paths);

	std::cout <<paths << std::endl;


    // --------------------- ctDifference
	PolyTree polytree2;

	bool rc2 = c.Execute(ctDifference, 
            polytree2,
            pftNonZero, 
            pftNonZero);

    std::cout << "Execute polytree difference result: " << rc2 << std::endl;
	std::cout << polytree2.Total() << std::endl;
    Paths paths2;
	OpenPathsFromPolyTree(polytree2, paths2);

	std::cout <<paths2 << std::endl;


    return 0;
}

int main() {
	test_combine();
	test_open_paths_combine();

	return 0;
}