# pycut
clone of jscut  in python - work in progress -

![pycut1](https://user-images.githubusercontent.com/28778239/226173273-8989a03e-e9d6-4753-9ade-17af9e15d4c3.png)

Note: the project has advanced nicely during the last holidays (24.12.2021), but there are certainly many many bugs.

Disclamer: This software is used at the user's own risk. No responsibility is accepted by its creator.

USAGE: start the program from the installation folder

> python pycut.py

> python pycut.py -h

> python pycut.py [<path_to_job>]

Dependencies: Python 3.10
- PySide6-6.3.0
- svgpathtools (latest) - pip installation bundled with numpy/scipy
- svgelements (latest) - used in the svgresolver.py utility
- freetype-py (latest) - used in svgtext2svpath.py utility
- shapely (1.8.2) with PyOpenGL
- matplotlib (to debug/view shapely offsets ops)

DONE:
- read "config" files : so-called job file with all settings and ops
- select 1 or more ops in the list and "generate" Gcode -> toolpaths OK for
   + pocket   YES
   + outside  YES
   + inside   YES
   + engrave  YES
   + vPocket   NO  (will never be implemented - I do not need this -)
- svg items selection and new op with combinaison Union/Diff/Inter/Xor (geometry calculated)
- preview geom displayed in svg viewer
- tabs
- toolpaths displayed in svg viewer
- gcode produced
- gcode viewer (as in Candle)
- gcode simulator (as in jsCut)

BUGS:
- and all the rest!

MAIN IMPROVMENTS OVER JSCUT
- tabs "on the fly" (no need to define them in the svg file)
- flip X/Y in GCode (good for my machine - the "1419" one -)
- can handle polygons as well as lines ("opened paths")

TODO:
- better settings
- what else ??

See the Wiki page for more.

