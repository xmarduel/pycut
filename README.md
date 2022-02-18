# pycut
clone of jscut  in python - work in progress -

Note: the project has advanced nicely during the last holidays (24.12.2022), but there are certainly many many bugs.

USAGE: start the program from the installation folder

> python pycut.py


Dependencies: Python
- PySide6-6.2.1
- svgpathtools (latest) - pip installation bundled with numpy/scipy
- shapely (1.8.0)
- matplotlib (for debugging)

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

BUGS:
- still cannot completely read Inkscape svg files because of all the Inkscape "garbage" with sodipodi namspaces etc.
- and all the rest!

TODO:
- capability to read text without converting them first to paths 
- svg "structure viewer" with check boxes for item(s) selection as alternative to svg viewer selection(s)

WILL NEVER BE IMPLEMENTED:
- vPocket (I do not need them)

