# pycut
clone of jscut in python

![pycut1](https://user-images.githubusercontent.com/28778239/226173273-8989a03e-e9d6-4753-9ade-17af9e15d4c3.png)



Disclamer: This software is used at the user's own risk. No responsibility is accepted by its creator.

Usage
-----
start the program from the installation folder

```
> python pycut.py
> python pycut.py -h
> python pycut.py [<path_to_job>]
> python pycut.py -g <path_to_gcode>
```

Dependencies
------------
- Python 3.10
- PySide6 6.4.3
- shapely 1.8.4 with PyOpenGL
- svgelements (latest)
- lxml (latest)
- freetype-py (latest) - used in svgtext2svpath.py utility
- matplotlib 3.6.2 (to debug/view shapely offsets ops)
- numba (latest) - for python simulator optimisation


Features
--------
- read "config" files : so-called job file with all settings and ops
- select 1 or more ops in the list and "generate" Gcode -> toolpaths OK for
   + pocket   YES
   + outside  YES
   + inside   YES
   + engrave  YES
   + vPocket   NO  (will never be implemented - I do not need this -)
   + drill or peck YES (for circle of radius smaller than the cutter radius)
- svg items selection and new op with combinaison Union/Diff/Inter/Xor (geometry calculated)
- preview geom displayed in svg viewer
- tabs
- toolpaths displayed in svg viewer
- gcode produced
- gcode viewer (as in Candle)
- gcode simulator (as in jsCut, but with candle parser)

Main Improvments over JsCut
---------------------------
- tabs "on the fly" (no need to define them in the svg file)
- flip X/Y in GCode (good for my machine - the "1419" one -)
- can handle polygons as well as lines ("closed paths" and "opened paths")


See the Wiki page for more.

