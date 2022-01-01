# pycut
clone of jscut  in python - only the very beginning - work in progress - windows only (because of clipper c++ extension modules)


DONE: what is currently working: basic
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

IN PROGRESS:
- tabs (actually only GUI: display & edit them)

TODO/BUGS:
- all the rest!
- improve clipper swig wrapper (make it more pythonic)
- in op lists: list of paths editable (comboboxes with checkboxes, label show the list of paths names)
- g code simulator with opencamlib ? seems powerfull and there is a python wrapper (the doc says) 

WILL NEVER BE IMPLEMENTED
- vPocket (I do not need them)


=========================================================================

Tabs are defined with: 
  - center (x,y)
  - radius r
  - global height (from bottom ie op cut depth)
  
Clipper also handles the case of "opened" lines with diff with closed polygons.
This is what is needed for the tabs handling.
Unfortunately clipper-6.1.3 gives wrong results (missing parts of the line), 
whereas clipper-6.4.2 gives good (better) results.

Still, the calculated "separated paths" are not optimal, there is from my side
a post-process step consisting of merging the "separated paths" when possible.

All in all, I've just tested tabs in a few cases, but the gcode simulation/viewer
can help checking the results.

This forces me to have 2 versions of the clipperlib python wrapper, 
because the 6.1.3 seems better when combining paths (not so much interpolated points)...

HINT: actually buggy, cannot mix the two clipper versions, so using 6.4.2 with too many
clipper points generated at offset execution, but tabs separation OK

Note: jsCut does not utilize clipper for the tabs handling, 
but an other c++ wrapper. 

=========================================================================
