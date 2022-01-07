import sys

'''
test svgpathtools:

can it read the svg basic shapes:
  <circle>
  <ellipse>
  <rect>
  <polygon>
  <polylines>
  <line>
  <path>


note1: 
  <rect> : with rounded corner : there is actually a patch in pull request
note2:
  <text> : https://catherineh.github.io/programming/2018/02/01/text-to-svg-paths ?
  
'''

import svgpathtools


def main(filename: str):
    paths, attributes, svg_attributes = svgpathtools.svg2paths(filename, return_svg_attributes=True)
    print("svg2paths ->", svg_attributes)

    # Let's print out the first path object and the color it was in the SVG
    # We'll see it is composed of two CubicBezier objects and, in the SVG file it 
    # came from, it was red
    for k, path in enumerate(paths):
        attribs = attributes[k]
        print("============= path %s =================" % attribs['id'])
        print(path)
        print(attribs)

    # and output
    svgpathtools.wsvg(paths, attributes=attributes, svg_attributes=svg_attributes, filename="out.svg")


if __name__ == '__main__':
    filename = sys.argv[1]
    main(filename)