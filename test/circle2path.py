def circle2path(cx, cy, r):
    return f"M {cx} {cy} m -{r} 0 a {r} {r} 0 1,1 {2*r} 0 a {r} {r} 0 1,1 -{2*r},0"

def main():
    r = 3.0
    cx = 110 - 3
    cy = 10.0 + 3
    sol = circle2path(cx, cy, 3)
    print(sol)

    r = 3.0
    cx = 110 - 3 + 0.8786
    cy = 10.0 + 3 - 0.8786
    sol = circle2path(cx, cy, 3)
    print(sol)
    

    
if __name__ == '__main__':
    main()
    
    
"""

M 54 13 a 3 3 0 1 1 6 0 a 3 3 0 1 1 -6 0 m 0 34 a 3 3 0 1 1 6 0 a 3 3 0 1 1 -6 0 m -44 0 a 3 3 0 1 1 6 0 a 3 3 0 1 1 -6 0 m 0 -34 a 3 3 0 1 1 6 0 a 3 3 0 1 1 -6 0 m 0 -3 H 60 V 50 H 10 V 10 M 55.7574 10 a 1 1 0 1 1 4.2426 4.2426 v 31.5148 a 1 1 0 1 1 -4.2426 4.2426 h -41.5148 a 1 1 0 1 1 -4.2426 -4.2426 v -31.5148 a 1 1 0 1 1 4.2426 -4.2426
"""