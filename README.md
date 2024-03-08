# pycut

clone of jscut in python

![pycut1](https://user-images.githubusercontent.com/28778239/226173273-8989a03e-e9d6-4753-9ade-17af9e15d4c3.png)

Disclamer: This software is used at the user's own risk. No responsibility is accepted by its creator.

## Usage

start the program from the installation folder

```
> python pycut.py -h
> python pycut.py
> python pycut.py -j <path_to_job>
> python pycut.py -g <path_to_gcode>
```

## Dependencies

- Python 3.10
- PySide6 6.6.2
- shapely 1.8.4 with PyOpenGL (latest)
- svgelements (latest)
- lxml (latest)
- freetype-py (latest) - used in svgtext2svgpath.py utility
- matplotlib (latest) - to debug/view shapely offsets ops
- numba (latest) - for python simulator optimization
- pyvoronoi (latest) - for HSM nibbler toolpaths

## Features

- read "config" files : so-called job file with all settings and ops
- select 1 or more ops in the list and "generate" Gcode -> toolpaths OK for
  - pocket YES
  - outside YES
  - inside YES
  - engrave YES
  - vPocket NO (will never be implemented - I do not need this -)
  - drill or peck YES (for circle of radius smaller than the cutter radius)
  - helix YES
- svg items selection and op creation with combinaison Union/Diff/Inter/Xor (geometry calculated)
- preview geom displayed in svg viewer
- tabs
- toolpaths displayed in svg viewer
- gcode path viewer (as in Candle)
- gcode simulator (as in jsCut, but with candle parser)
- gcode produced (GRBL)

## Main Improvments over JsCut

- tabs "on the fly" (no need to define them in the svg file)
- flip X/Y in GCode (good for my machine - the "1419" one -)
- can handle polygons as well as lines ("closed paths" and "opened paths")
- ![new](RESOURCES/new_img.png) toolpaths with HSM_nibblers optional

See the Wiki page for more.
