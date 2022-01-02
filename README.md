# pycut
clone of jscut  in python - work in progress -

Note: the project has advanced nicely during the last holidays, but there are certainly many many bugs.

USAGE: start the program from the installation folder (because of clipper c++ extension modules only for windows)

> python main.py

Installation: env variables required:
 + %PYCUT%  : the installation folder
 + %PYTHONPATH% : with %PYCUT%\clipper_642 and %PYCUT%\clipper_613  

Python Dependencies:
- PySide6
- svgpathtools
- numpy

DONE: basic
- read "config" files : so-called job file with all settings and ops
- select 1 or more ops in the list and "generate" Gcode -> toolpaths OK for
   + pocket   YES
   + outside  YES
   + inside   YES
   + engrave  YES
   + vPocket   NO
- svg items selection and new op with combinaison (geometry calculated)
- preview geom displayed in svg viewer
- toolpaths displayed in svg viewer
- gcode produced
- gcode viewer (as in Candle)
- gcode simulator (as in jsCut)
- tabs

TODO/BUGS:
- all the rest!
- improve clipper swig wrapper (make it more pythonic)
- in op lists: list of paths editable (comboboxes with checkboxes, label show the list of paths names)
- g code simulator with opencamlib ? seems powerfull and there is a python wrapper (the doc says) 

WILL NEVER BE IMPLEMENTED
- vPocket (I do not need them)


Note on the Clipper Library: version used is 6.4.2. 
===================================================

Clipper also handles the case of "opened" lines with diff with closed polygons.
This is what is needed for the tabs handling.
Unfortunately clipper-6.1.3 gives wrong results (missing parts of the line), 
whereas clipper-6.4.2 gives good (better) results.

Still, the calculated "separated paths" are not optimal, there is from my side
a post-process step consisting of merging the "separated paths" when possible.

All in all, I've just tested tabs in a few cases, but the gcode simulation/viewer
can help checking the results.

So the version 6.4.2 is used, but produces more points when offseting than the 6.1.3
version

PS: jsCut does not utilize clipper for the tabs handling, 
but an other c++ wrapper. 

