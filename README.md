# pycut
clone of jscut  in python - only the very beginning - work in progress - windows only (because of extension modules)


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


==============================================================================
Tab Algorithm:  Infact not that wild (I think)

tabs are defined with: 
  - center (x,y)
  - radius r
  - global height (from bottom ie op cut depth)

When generating GCode (segment per segment, building G1 commands):

- current pos (xo,yo,zo)
- check next pos (x,y,zo)
    - if not in TAB  -> generate normat G1 x,y
    - if in TAB      -> current zo stored as "z_ref"

        0. get pos at tab border (xt,yt)
        1. normal G1 to TAB border xt,yt,z_ref
        2. G1 z_ok (defined by tab height above bottom)

        current is (xt,yt,z_ok)

    |-> check next pos (x,y,z_ok)  (probably in TAB if small segment)
    |
    |
    |      if in TAB  
    |      1. G1 x,y,z_ok   // attention it could in 1 move leave the tab and enter another one... FIXME
    ----------                         // check step length vs tab size
                                       if in_same_tab : Ok... no problem
                                       if not in same tab: ZUT : TODO

           if not in TAB (is TAB "end")
           0. get pos at tab border (xt,yt)
           1. normal G1 to TAB border xt,yt,z_ok
           2. G1 z_ref
           3. G1 x,y

