
from typing import List

#import clipper_613 as ClipperLib
import clipper_642 as ClipperLib

class ClipperUtils:
    '''
    Wrapper functions on ClipperLib
    '''
    print("Using ClipperLib version %s" % ClipperLib.CLIPPER_VERSION)

    inchToClipperScale = 100000  # Scale inch to Clipper
    cleanPolyDist = inchToClipperScale / 100000
    # clipper-6.1.3
    arcTolerance = 2.5 # -> ok, like jscut
    
    # clipper-6.4.2 ?? strange I don't known the rght settigns
    if ClipperLib.CLIPPER_VERSION == '6.4.2':
        # -> much too fine, but increasing produces loss bad of precision
        arcTolerance = 2.5
    

    @classmethod
    def simplifyAndClean(cls, geometry: ClipperLib.PathVector, fillRule: ClipperLib.PolyFillType) -> ClipperLib.PathVector :
        '''
        Simplify and clean up Clipper geometry
        '''
        ClipperLib.CleanPolygons(geometry, cls.cleanPolyDist)
        ClipperLib.SimplifyPolygons(geometry, fillRule)

        return geometry

    @classmethod
    def clip (cls, paths1: ClipperLib.PathVector, paths2: ClipperLib.PathVector, clipType: ClipperLib.ClipType) -> ClipperLib.PathVector:
        '''
        Clip Clipper geometry. clipType is a ClipperLib.ClipType constant. Returns new geometry.
        '''
        clipper = ClipperLib.Clipper()
        clipper.AddPaths(paths1, ClipperLib.PolyType.ptSubject, True)
        clipper.AddPaths(paths2, ClipperLib.PolyType.ptClip, True)
        
        result = ClipperLib.PathVector()
        clipper.Execute(clipType, result, ClipperLib.PolyFillType.pftEvenOdd, ClipperLib.PolyFillType.pftEvenOdd)
        
        return result

    @classmethod
    def diff(cls, paths1: ClipperLib.PathVector, paths2: ClipperLib.PathVector) -> ClipperLib.PathVector:
        '''
        Return difference between to Clipper geometries. Returns new geometry.
        '''
        return cls.clip(paths1, paths2, ClipperLib.ClipType.ctDifference)

    @classmethod
    def offset(cls, geometry: ClipperLib.PathVector, amount: float, joinType=None, endType=None):
        '''
        '''
        if joinType is None:
            joinType = ClipperLib.JoinType.jtRound
        if endType is None:
            endType = ClipperLib.EndType.etClosedPolygon

        # bug workaround: join types are swapped in ClipperLib 6.1.3.2
        if joinType == ClipperLib.JoinType.jtSquare:
            joinType = ClipperLib.JoinType.jtMiter
        elif joinType == ClipperLib.JoinType.jtMiter:
            joinType = ClipperLib.JoinType.jtSquare

        co = ClipperLib.ClipperOffset(2, cls.arcTolerance)
        co.AddPaths(geometry, joinType, endType)
        
        offsetted = ClipperLib.PathVector()
        co.Execute(offsetted, amount)

        # 6.4.2 -> need clean !
        ClipperLib.CleanPolygons(offsetted, ClipperUtils.cleanPolyDist)
        return offsetted

    @classmethod
    def combine(cls, clipper_path: ClipperLib.IntPointVector, clipper_paths: List[ClipperLib.IntPointVector], clipType: ClipperLib.ClipType) -> ClipperLib.PathVector:
        '''
        '''
        subj = ClipperLib.PathVector()
        subj.append(clipper_path)

        # special case : nothing to combine 
        if len(clipper_paths) == 0:
            return subj

        clip = ClipperLib.PathVector()
        for path in clipper_paths:
            clip.append(path)

        c = ClipperLib.Clipper()

        c.AddPaths(subj, ClipperLib.PolyType.ptSubject, True)
        c.AddPaths(clip, ClipperLib.PolyType.ptClip, True)
    
        combined_clipper_paths = ClipperLib.PathVector()

        c.Execute(clipType, 
                combined_clipper_paths,
                ClipperLib.PolyFillType.pftNonZero, 
                ClipperLib.PolyFillType.pftNonZero)

        return combined_clipper_paths

    @classmethod
    def crosses(cls, bounds, p1: ClipperLib.IntPoint, p2: ClipperLib.IntPoint):
        '''
        Does the line from p1 to p2 cross outside of bounds?
        '''
        if bounds == None:
            return True
        if p1.X == p2.X and p1.Y == p2.Y :
            return False

        clipper = ClipperLib.Clipper()
        # JSCUT clipper.AddPath([p1, p2], ClipperLib.PolyType.ptSubject, False)
        # JSCUT clipper.AddPaths(bounds, ClipperLib.PolyType.ptClip, True)

        p1_p2 = ClipperLib.IntPointVector()
        p1_p2.append(p1)
        p1_p2.append(p2)

        clipper.AddPath(p1_p2, ClipperLib.PolyType.ptSubject, False)
        clipper.AddPaths(bounds, ClipperLib.PolyType.ptClip, True)

        result = ClipperLib.PolyTree()
        clipper.Execute(ClipperLib.ClipType.ctIntersection, result, ClipperLib.PolyFillType.pftEvenOdd, ClipperLib.PolyFillType.pftEvenOdd)
    
        if result.ChildCount() == 1:
            child : ClipperLib.PolyNode = result.GetFirst() 
            points = child.Contour
            if len(points) == 2:
                if points[0].X == p1.X and points[1].X == p2.X and points[0].Y == p1.Y and points[1].Y == p2.Y :
                    return False
                if points[0].X == p2.X and points[1].X == p1.X and points[0].Y == p2.Y and points[1].Y == p1.Y :
                    return False

        return True

    @classmethod
    def openpath_remove_tabs(cls, clipper_path: ClipperLib.IntPointVector, clipper_polygons_path: List[ClipperLib.IntPointVector]) -> ClipperLib.PathVector:
        '''
        the resulting paths canbe "unordered", this is a bit ennoying

        -> we re-order them, so that the first path of the output paths
        contains the first point of the input path TODO
        '''
        c = ClipperLib.Clipper()
        c.AddPath(clipper_path, ClipperLib.PolyType.ptSubject, False)  # open path
        c.AddPaths(clipper_polygons_path, ClipperLib.PolyType.ptClip, True)

        polytree = ClipperLib.PolyTree()

        c.Execute(ClipperLib.ClipType.ctDifference, 
            polytree,
            ClipperLib.PolyFillType.pftNonZero, 
            ClipperLib.PolyFillType.pftNonZero)

        paths = ClipperLib.PathVector()
        ClipperLib.OpenPathsFromPolyTree(polytree, paths)

        return paths

    @classmethod
    def clone_pathvector(cls, path: ClipperLib.PathVector) -> ClipperLib.PathVector:
        '''
        '''
        clone = ClipperLib.PathVector()

        for intvector in path:
            iv_clone = ClipperUtils.clone_intpointvector(intvector)
            clone.append(iv_clone)

        return clone

    @classmethod
    def clone_intpointvector(cls, vector: ClipperLib.IntPointVector) -> ClipperLib.IntPointVector:
        '''
        '''
        clone = ClipperLib.IntPointVector()

        for pt in vector:
            pt_clone = ClipperLib.IntPoint(pt.X, pt.Y)
            clone.append(pt_clone)

        return clone