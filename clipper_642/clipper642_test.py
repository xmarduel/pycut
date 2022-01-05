import clipper_642 as clipper

'''
This version handle better the diff of open lines vs closed polygons,
what we need the the toolpaths when there are tabs! 
'''

def test_openline_diff():
    '''
       - subject is an open line
       - clippers are the (closed) tabs
    
       - result is a list of open lines, where none of their parts
       are in the tab
    '''
    print("test_openline_diff")

    line = clipper.IntPointVector()
    line.append(clipper.IntPoint(100,100))
    line.append(clipper.IntPoint(600,100))
    line.append(clipper.IntPoint(600,600))
    line.append(clipper.IntPoint(100,600))
    line.append(clipper.IntPoint(100,100)) # close the path! but give it as "opened"

    tab1 = clipper.IntPointVector()
    tab1.append(clipper.IntPoint(200,80))
    tab1.append(clipper.IntPoint(300,80))
    tab1.append(clipper.IntPoint(300,120))
    tab1.append(clipper.IntPoint(200,120))

    tab2 = clipper.IntPointVector()
    tab2.append(clipper.IntPoint( 80,200))
    tab2.append(clipper.IntPoint(120,200))
    tab2.append(clipper.IntPoint(120,300))
    tab2.append(clipper.IntPoint( 80,300))

    # tab3
    tab3 = clipper.IntPointVector()
    tab3.append(clipper.IntPoint(580,200))
    tab3.append(clipper.IntPoint(620,200))
    tab3.append(clipper.IntPoint(620,300))
    tab3.append(clipper.IntPoint(580,300))
    
    tabs = clipper.PathVector()
    tabs.append(tab1)
    tabs.append(tab2)
    tabs.append(tab3)


    c = clipper.Clipper()
    c.AddPath(line, clipper.PolyType.ptSubject, False)
    c.AddPaths(tabs, clipper.PolyType.ptClip, True)

    polytree = clipper.PolyTree()

    c.Execute(clipper.ClipType.ctDifference, 
            polytree,
            clipper.PolyFillType.pftNonZero, 
            clipper.PolyFillType.pftNonZero)

    print("Test OpenLine Difference with Tabs")
    print("Resulting # paths:", polytree.Total())

    paths = clipper.PathVector()
    clipper.OpenPathsFromPolyTree(polytree, paths)

    print(paths)

def test_openline_diff_simple_segment():
    '''
       - subject is an open line
       - clippers are the (closed) tabs
    
       - result is a list of open lines, where none of their parts
       are in the tab
    '''
    print("test_openline_diff")

    line = clipper.IntPointVector()
    #line.append(clipper.IntPoint(100,100))
    #line.append(clipper.IntPoint(600,100))
    #line.append(clipper.IntPoint(600,600))
    line.append(clipper.IntPoint(100,600))
    line.append(clipper.IntPoint(100,100))

    tab1 = clipper.IntPointVector()
    tab1.append(clipper.IntPoint(200,80))
    tab1.append(clipper.IntPoint(250,80))
    tab1.append(clipper.IntPoint(250,120))
    tab1.append(clipper.IntPoint(200,120))
    #tab1.append(clipper.IntPoint(200,80))

    tab2 = clipper.IntPointVector()
    tab2.append(clipper.IntPoint(400,80))
    tab2.append(clipper.IntPoint(450,80))
    tab2.append(clipper.IntPoint(450,120))
    tab2.append(clipper.IntPoint(400,120))
    #tab2.append(vIntPoint(400,80))

    # tab3 is oberlapping tab2...
    tab3 = clipper.IntPointVector()
    tab3.append(clipper.IntPoint(420,80))
    tab3.append(clipper.IntPoint(470,80))
    tab3.append(clipper.IntPoint(470,120))
    tab3.append(clipper.IntPoint(420,120))
    #tab3.append(vIntPoint(400,80))
    
    tabs = clipper.PathVector()
    tabs.append(tab1)
    tabs.append(tab2)
    #tabs.append(tab3)


    c = clipper.Clipper()
    c.AddPath(line, clipper.PolyType.ptSubject, False)
    c.AddPaths(tabs, clipper.PolyType.ptClip, True)

    polytree = clipper.PolyTree()

    c.Execute(clipper.ClipType.ctDifference, 
            polytree,
            clipper.PolyFillType.pftNonZero, 
            clipper.PolyFillType.pftNonZero)

    print("Test OpenLine Last Segment Difference with Tabs")
    print("Resulting # paths:", polytree.Total())

    paths = clipper.PathVector()
    clipper.OpenPathsFromPolyTree(polytree, paths)

    print(paths)

    rpaths = clipper.PathVector()
    for path in paths:
        lp = list(path)
        lp.reverse()
        rpaths.append(lp)

    print(rpaths)

if __name__ == '__main__':
    print("CLIPPER VERSION", clipper.CLIPPER_VERSION)
    
    test_openline_diff()

    test_openline_diff_simple_segment()
