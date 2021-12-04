
from typing import List

import clipper.clipper as ClipperLib


class ClipperUtils:
    '''
    Wrapper functions on ClipperLib
    '''
    inchToClipperScale = 100000  # Scale inch to Clipper
    cleanPolyDist = inchToClipperScale / 100000
    arcTolerance = inchToClipperScale / 40000

    @classmethod
    def simplifyAndClean(cls, geometry: ClipperLib.PathVector, fillRule: ClipperLib.PolyFillType) -> ClipperLib.PathVector :
        '''
        Simplify and clean up Clipper geometry
        '''
        geometry = ClipperLib.CleanPolygons(geometry, cls.cleanPolyDist)
        geometry = ClipperLib.SimplifyPolygons(geometry, fillRule)

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
        clipper.Execute(clipType, result, ClipperLib.PolyFillType.pftEvenOdd, ClipperLib.PolyFillType.pftEvenOdd);
        
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

        #offsetted = ClipperLib.Clipper.CleanPolygons(offsetted, cleanPolyDist);
        return offsetted

    @classmethod
    def combine(cls, clipper_paths: List[ClipperLib.IntPointVector], clipType: ClipperLib.ClipType) -> ClipperLib.PathVector:
        '''
        '''
        subj = ClipperLib.PathVector()
        subj.append(clipper_paths[0])

        # special case : only 1 path selected 
        if len(clipper_paths) == 1:
            return subj

        clip = ClipperLib.PathVector()
        for path in clipper_paths[1:]:
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
        clipper.AddPath([p1, p2], ClipperLib.PolyType.ptSubject, False)
        clipper.AddPaths(bounds, ClipperLib.PolyType.ptClip, True)

        result = ClipperLib.PolyTree()
        clipper.Execute(ClipperLib.ClipType.ctIntersection, result, ClipperLib.PolyFillType.pftEvenOdd, ClipperLib.PolyFillType.pftEvenOdd)
    
        if result.ChildCount() == 1:
            child : ClipperLib.PolyNode = result.Childs[0] 
            points = child.Contour
            if len(points) == 2:
                if points[0].X == p1.X and points[1].X == p2.X and points[0].Y == p1.Y and points[1].Y == p2.Y :
                    return False
                if points[0].X == p2.X and points[1].X == p1.X and points[0].Y == p2.Y and points[1].Y == p1.Y :
                    return False

        return True

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

        for intpt in vector:
            pt_clone = ClipperLib.IntPoint(intpt.X, intpt.Y)
            clone.append(pt_clone)

        return clone