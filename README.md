# pycut
clone of jscut  in python - only the very beginning


what is currently working: basic
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

TODO/BUGS:
- all the rest!
- tabs completely ignored
- vPocket ?
- improve clipper swig wrapper (make it more pythonic)
- should only select svg paths in viewer from the initial svg (not the generated preview geometry/toolpaths)