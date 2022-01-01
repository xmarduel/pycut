
from typing import List

import clipper_613 as Clipper613Lib
import clipper_642 as Clipper642Lib

class ClipperUtils:
    '''
    Wrapper functions on Clipper613Lib
    '''
    print("Using Clipper613Lib version %s" % Clipper613Lib.CLIPPER_VERSION)

    inchToClipperScale = 100000  # Scale inch to Clipper
    cleanPolyDist = inchToClipperScale / 100000
    # clipper-6.1.3
    arcTolerance = 2.5 # -> ok, like jscut
    
    # clipper-6.4.2 ?? strange I don't known the rght settigns
    if Clipper613Lib.CLIPPER_VERSION == '6.4.2':
        # -> much too fine, but increasing produces loss bad of precision
        arcTolerance = 2.5
    

    @classmethod
    def simplifyAndClean(cls, geometry: Clipper613Lib.PathVector, fillRule: Clipper613Lib.PolyFillType) -> Clipper613Lib.PathVector :
        '''
        Simplify and clean up Clipper geometry
        '''
        Clipper613Lib.CleanPolygons(geometry, cls.cleanPolyDist)
        Clipper613Lib.SimplifyPolygons(geometry, fillRule)

        return geometry

    @classmethod
    def clip (cls, paths1: Clipper613Lib.PathVector, paths2: Clipper613Lib.PathVector, clipType: Clipper613Lib.ClipType) -> Clipper613Lib.PathVector:
        '''
        Clip Clipper geometry. clipType is a Clipper613Lib.ClipType constant. Returns new geometry.
        '''
        clipper = Clipper613Lib.Clipper()
        clipper.AddPaths(paths1, Clipper613Lib.PolyType.ptSubject, True)
        clipper.AddPaths(paths2, Clipper613Lib.PolyType.ptClip, True)
        
        result = Clipper613Lib.PathVector()
        clipper.Execute(clipType, result, Clipper613Lib.PolyFillType.pftEvenOdd, Clipper613Lib.PolyFillType.pftEvenOdd)
        
        return result

    @classmethod
    def diff(cls, paths1: Clipper613Lib.PathVector, paths2: Clipper613Lib.PathVector) -> Clipper613Lib.PathVector:
        '''
        Return difference between to Clipper geometries. Returns new geometry.
        '''
        return cls.clip(paths1, paths2, Clipper613Lib.ClipType.ctDifference)

    @classmethod
    def offset(cls, geometry: Clipper613Lib.PathVector, amount: float, joinType=None, endType=None):
        '''
        '''
        if joinType is None:
            joinType = Clipper613Lib.JoinType.jtRound
        if endType is None:
            endType = Clipper613Lib.EndType.etClosedPolygon

        # bug workaround: join types are swapped in Clipper613Lib 6.1.3.2
        if joinType == Clipper613Lib.JoinType.jtSquare:
            joinType = Clipper613Lib.JoinType.jtMiter
        elif joinType == Clipper613Lib.JoinType.jtMiter:
            joinType = Clipper613Lib.JoinType.jtSquare

        co = Clipper613Lib.ClipperOffset(2, cls.arcTolerance)
        co.AddPaths(geometry, joinType, endType)
        
        offsetted = Clipper613Lib.PathVector()
        co.Execute(offsetted, amount)

        # 6.4.2 -> need clean !
        Clipper613Lib.CleanPolygons(offsetted, ClipperUtils.cleanPolyDist)
        return offsetted

    @classmethod
    def combine(cls, clipper_paths: List[Clipper613Lib.IntPointVector], clipType: Clipper613Lib.ClipType) -> Clipper613Lib.PathVector:
        '''
        '''
        subj = Clipper613Lib.PathVector()
        subj.append(clipper_paths[0])

        # special case : only 1 path selected 
        if len(clipper_paths) == 1:
            return subj

        clip = Clipper613Lib.PathVector()
        for path in clipper_paths[1:]:
            clip.append(path)

        c = Clipper613Lib.Clipper()

        c.AddPaths(subj, Clipper613Lib.PolyType.ptSubject, True)
        c.AddPaths(clip, Clipper613Lib.PolyType.ptClip, True)
    
        combined_clipper_paths = Clipper613Lib.PathVector()

        c.Execute(clipType, 
                combined_clipper_paths,
                Clipper613Lib.PolyFillType.pftNonZero, 
                Clipper613Lib.PolyFillType.pftNonZero)

        return combined_clipper_paths

    @classmethod
    def crosses(cls, bounds, p1: Clipper613Lib.IntPoint, p2: Clipper613Lib.IntPoint):
        '''
        Does the line from p1 to p2 cross outside of bounds?
        '''
        if bounds == None:
            return True
        if p1.X == p2.X and p1.Y == p2.Y :
            return False

        clipper = Clipper613Lib.Clipper()
        # JSCUT clipper.AddPath([p1, p2], Clipper613Lib.PolyType.ptSubject, False)
        # JSCUT clipper.AddPaths(bounds, Clipper613Lib.PolyType.ptClip, True)

        p1_p2 = Clipper613Lib.IntPointVector()
        p1_p2.append(p1)
        p1_p2.append(p2)

        clipper.AddPath(p1_p2, Clipper613Lib.PolyType.ptSubject, False)
        clipper.AddPaths(bounds, Clipper613Lib.PolyType.ptClip, True)

        result = Clipper613Lib.PolyTree()
        clipper.Execute(Clipper613Lib.ClipType.ctIntersection, result, Clipper613Lib.PolyFillType.pftEvenOdd, Clipper613Lib.PolyFillType.pftEvenOdd)
    
        if result.ChildCount() == 1:
            child : Clipper613Lib.PolyNode = result.GetFirst() 
            points = child.Contour
            if len(points) == 2:
                if points[0].X == p1.X and points[1].X == p2.X and points[0].Y == p1.Y and points[1].Y == p2.Y :
                    return False
                if points[0].X == p2.X and points[1].X == p1.X and points[0].Y == p2.Y and points[1].Y == p1.Y :
                    return False

        return True

    @classmethod
    def openpath_remove_tabs(cls, clipper_path: Clipper613Lib.IntPointVector, clipper_polygons_path: List[Clipper613Lib.IntPointVector]) -> Clipper613Lib.PathVector:
        '''
        the resulting paths canbe "unordered", this is a bit ennoying

        -> we re-order them, so that the first path of the output paths
        contains the first point of the input path TODO
        '''
        c = Clipper642Lib.Clipper()
        c.AddPath(clipper_path, Clipper642Lib.PolyType.ptSubject, False)  # open path
        c.AddPaths(clipper_polygons_path, Clipper642Lib.PolyType.ptClip, True)

        polytree = Clipper642Lib.PolyTree()

        c.Execute(Clipper642Lib.ClipType.ctDifference, 
            polytree,
            Clipper642Lib.PolyFillType.pftNonZero, 
            Clipper642Lib.PolyFillType.pftNonZero)

        paths = Clipper642Lib.PathVector()
        Clipper642Lib.OpenPathsFromPolyTree(polytree, paths)

        return paths

    @classmethod
    def clone_pathvector(cls, path: Clipper613Lib.PathVector) -> Clipper613Lib.PathVector:
        '''
        '''
        clone = Clipper613Lib.PathVector()

        for intvector in path:
            iv_clone = ClipperUtils.clone_intpointvector(intvector)
            clone.append(iv_clone)

        return clone

    @classmethod
    def clone_intpointvector(cls, vector: Clipper613Lib.IntPointVector) -> Clipper613Lib.IntPointVector:
        '''
        '''
        clone = Clipper613Lib.IntPointVector()

        for intpt in vector:
            pt_clone = Clipper613Lib.IntPoint(intpt.X, intpt.Y)
            clone.append(pt_clone)

        return clone