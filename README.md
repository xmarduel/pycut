# pycut
clone of jscut  in python - only the very beginning


what is currently working:
- read "config" files : so called job file with all settings -> GUI updated
- select 1 op  in the list and "generate" Gcode -> toolpath OK for
   + pocket   YES
   + outside   NO
   + inside    NO
   + engrave   NO
   + vPocket   NO
- svg items selection and new op with combinaison (geometry calculated)



BUGS:
- all the rest
- tabs completely ignored
- should only select svg path in viewer from the initial svg (not the generated paths)

- improve clipper swig wrapper (make it more pythonic)
