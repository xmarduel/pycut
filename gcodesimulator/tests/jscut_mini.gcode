G21         ; Set units to mm
G90         ; Absolute positioning
G1 Z5 F2500      ; Move to clearance level

;
; Operation:    0
; Name:         ee
; Type:         Engrave
; Paths:        1
; Direction:    Conventional
; Cut Depth:    3
; Pass Depth:   3
; Plunge rate:  250
; Cut rate:     1000
;

; Path 0
; Rapid to initial position
G1 X85.3333 Y-21.3335 F2500
G1 Z0.0000
; plunge
G1 Z-3.0000 F250
; cut
G1 X21.3335 Y-21.3335 F1000
G1 X21.3335 Y-85.3333
G1 X85.3333 Y-85.3333
G1 X85.3333 Y-21.3335
G1 X85.3333 Y-21.3335
; Retract
G1 Z5.0000 F2500
