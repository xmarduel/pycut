# pycut
clone of jscut  in python - only the very beginning - work in progress - windows only (because of extension modules)


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
- gcode viewer (as in Candle)
- gcode simulator (as in jsCut)

TODO/BUGS:
- all the rest!
- tabs completely ignored
- vPocket ?
- improve clipper swig wrapper (make it more pythonic)
- in op lists: list of paths editable (comboboxes with checkboxes, label show the list of paths names)




Tab Algorithm:  Infact not that wild (I think)

tabs are defined : 
  - center
  - radius
  - height from bottom

GUI -> to do / read from a job file or add/delete/move interactively

When generating GCode (segment per segment, building G1 commands):

- current pos (x,y,z)
- check next pos (x,y,z)
    - if not in TAB  -> generate normat G1 x,y
    - if in TAB ->   state "IN_TAB"  (normal "z_ref" to store)

        1. normal G1 to TAB rand (entry) xt,yt,z_ref
        2. G1 Z_ok (defined by tab height above bottom)

        current is (xt,yt,z_ok)
    
    |-> check next pos (should be in TAB)
    |
    |      if in TAB  -> G1 x,y,z_ok   // attention it could in 1 move leave the tab and enter another one... FIXME
    ----------                         // check step length vs tab size
                                       if in_same_tab : Ok... no problem
                                       if not in same tab: ZUT : TODO

           if not in TAB (is TAB "end")
               1. get to tab rand (xt,yt)
                   -> G1 xt,yt,z_ok
                   -> G1 z_ref (stored "normal" height)
                   -> G1 x,y

                   state "NOT_IN_TAB"

