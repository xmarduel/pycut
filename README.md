# pycut
clone of jscut  in python - work in progress -

Note: the project has advanced nicely during the last holidays (24.12.2022), but there are certainly many many bugs.

USAGE: start the program from the installation folder (because of clipper c++ extension modules only for windows)

> python main.py

Installation: env variables required:
 + %PYCUT%  : the installation folder
 + %PYTHONPATH% : with %PYCUT%\clipper_642 and %PYCUT%\clipper_613  

Dependencies: Python
- PySide6-6.2.1
- svgpathtools (latest) - pip installation bundled with numpy

Dependencies: C++
- clipper-6.4.2 (sources in PyCut, SWIG wrapper built in PyCut)

DONE: basic
- read "config" files : so-called job file with all settings and ops
- select 1 or more ops in the list and "generate" Gcode -> toolpaths OK for
   + pocket   YES
   + outside  YES
   + inside   YES
   + engrave  YES
   + vPocket   NO
- svg items selection and new op with combinaison Union/Diff/Inter/Xor (geometry calculated)
- preview geom displayed in svg viewer
- toolpaths displayed in svg viewer
- gcode produced
- gcode viewer (as in Candle)
- gcode simulator (as in jsCut)
- tabs

TODO/BUGS:
- all the rest!
- improve clipper swig wrapper (make it more pythonic / better for debugging)
- in operations table: make list of paths editable (comboboxes with checkboxes, label showing the list of paths selected for the ops)
- g-code simulator with opencamlib ? seems powerfull and there is a python wrapper (the doc says) 

WILL NEVER BE IMPLEMENTED
- vPocket (I do not need them)

