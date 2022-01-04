import sys

import svgpathtools


def main(filename: str):
    paths, attributes, svg_attributes = svgpathtools.svg2paths(filename, return_svg_attributes=True)
    print("svg2paths2 ->", svg_attributes)

    # Let's print out the first path object and the color it was in the SVG
    # We'll see it is composed of two CubicBezier objects and, in the SVG file it 
    # came from, it was red
    for k, path in enumerate(paths):
        attribs = attributes[k]
        print("============= path %s =================" % attribs['id'])
        print(path)
        print(attribs)


if __name__ == '__main__':
    filename = sys.argv[1]
    main(filename)