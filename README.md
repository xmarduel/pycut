# pycut
clone of jscut  in python - only the very beginning


what is currently working:
- read "config" files : so called job file with all settings -> GUI updated
- select 1 op  in the list and "generate" Gcode -> toolpaths OK for
   + pocket   YES
   + outside  YES
   + inside   YES
   + engrave  YES
   + vPocket   NO
- svg items selection and new op with combinaison (geometry calculated)



TODO:
- all the rest
- tabs completely ignored


BUGS:
- improve clipper swig wrapper (make it more pythonic)
- should only select svg path in viewer from the initial svg (not the generated paths)