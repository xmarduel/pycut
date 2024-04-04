# PyCut

clone of jscut in python

![pycut](RESOURCES/pycut_img.png)

Disclamer: This software is used at the user's own risk. No responsibility is accepted by its creator.

## Why PyCut

With <strong>PyCut</strong>, you do not need to do 3D modelling. SVG files (2D) are <strong>PyCut</strong> input format, and for simple milling tasks it is perfectly OK. Granted, SVG shapes modelling is not so straightforward as one could think, as free software lacks good SVG modelling applications. Infact, writing a SVG file with a text editor is sometimes the best way! For complex shapes (so-called SVG paths), other tools may be used (see Tutorial).

Before starting, please have a look at the tutorial to be sure your SVG input files follow the PyCut requirements (mostly: how to define the view box).

## Usage

start the program from the installation folder

```
> python pycut.py -h
> python pycut.py
> python pycut.py -j <path_to_job>
> python pycut.py -g <path_to_gcode>   # view an external gcode data
```

## Dependencies

- Python 3.11
- PySide6 6.6.3
- shapely 1.8.5 
- PyOpenGL (latest)
- svgelement (latest)
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
- ![new](RESOURCES/new_img.png) toolpaths with HSM_nibblers optional.

See the Wiki page for more.
