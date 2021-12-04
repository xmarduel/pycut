import clipper

def test1():
    outer = clipper.IntPointVector()
    outer.append(clipper.IntPoint(180,200))
    outer.append(clipper.IntPoint(260,200))
    outer.append(clipper.IntPoint(260,150))
    outer.append(clipper.IntPoint(180,150))

    inner = clipper.IntPointVector()
    inner.append(clipper.IntPoint(215,160))
    inner.append(clipper.IntPoint(230,190))
    inner.append(clipper.IntPoint(200,190))

    subj = clipper.PathVector()
    subj.append(outer)
    subj.append(inner)

    clip = clipper.PathVector()
    clip_0 = clipper.IntPointVector()
    clip_0.append(clipper.IntPoint(190,210))
    clip_0.append(clipper.IntPoint(240,210))
    clip_0.append(clipper.IntPoint(240,130))
    clip_0.append(clipper.IntPoint(190,130))
    clip.append(clip_0)

    c = clipper.Clipper()

    c.AddPaths(subj, clipper.PolyType.ptSubject, True)
    c.AddPaths(clip, clipper.PolyType.ptClip, True)

    solution = clipper.PathVector()
    
    c.Execute(clipper.ClipType.ctIntersection, 
            solution,
            clipper.PolyFillType.pftNonZero, 
            clipper.PolyFillType.pftNonZero)

    clipper.dumpPaths("subj", subj)
    clipper.dumpPaths("clip", clip)
    clipper.dumpPaths("solution", solution)

def test(clipType: clipper.ClipType):
    c1 = clipper.IntPointVector()
    c1.append(clipper.IntPoint(20,20))
    c1.append(clipper.IntPoint(20,60))
    c1.append(clipper.IntPoint(60,60))
    c1.append(clipper.IntPoint(60,20))

    subj = clipper.PathVector()
    subj.append(c1)

    clip = clipper.PathVector()
    c2 = clipper.IntPointVector()
    c2.append(clipper.IntPoint(40,40))
    c2.append(clipper.IntPoint(40,80))
    c2.append(clipper.IntPoint(80,80))
    c2.append(clipper.IntPoint(80,40))
    clip.append(c2)

    c = clipper.Clipper()

    c.AddPaths(subj, clipper.PolyType.ptSubject, True)
    c.AddPaths(clip, clipper.PolyType.ptClip, True)

    solution = clipper.PathVector()
    
    c.Execute(clipType, 
            solution,
            clipper.PolyFillType.pftNonZero, 
            clipper.PolyFillType.pftNonZero)

    clipper.dumpPaths("subj", subj)
    clipper.dumpPaths("clip", clip)
    clipper.dumpPaths("solution", solution)

def  test_offset():
    outer = clipper.IntPointVector()
    outer.append(clipper.IntPoint(180,200))
    outer.append(clipper.IntPoint(260,200))
    outer.append(clipper.IntPoint(260,150))
    outer.append(clipper.IntPoint(180,150))

    subj = clipper.PathVector()
    subj.append(outer)

    joinType = clipper.JoinType.jtRound
    endType = clipper.EndType.etClosedPolygon

    co = clipper.ClipperOffset(2, 0.1)
    co.AddPaths(subj, joinType, endType)
        
    offsetted = clipper.PathVector()
    co.Execute(offsetted, -1)

    clipper.dumpPaths("offset input", subj)
    clipper.dumpPaths("solution offset", offsetted)

    #offsetted = ClipperLib.Clipper.CleanPolygons(offsetted, cleanPolyDist);
    return offsetted

if __name__ == '__main__':
    #test1()
    #test(clipper.ClipType.ctUnion)
    #test(clipper.ClipType.ctIntersection)
    #test(clipper.ClipType.ctXor)
    #test(clipper.ClipType.ctDifferences)

    test_offset()