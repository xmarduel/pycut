G21         ; Set units to mm
G90         ; Absolute positioning
G1 Z2.54 F2540      ; Move to clearance level




;
; Operation:    0
; Name:         
; Type:         Inside
; Paths:        1
; Direction:    Conventional
; Cut Depth:    3.175
; Pass Depth:   3.175
; Plunge rate:  127
; Cut rate:     1016
;

; Path 0
; Rapid to initial position
G1 X38.4124 Y-38.4124 F2540
G1 Z0.0000
; ramp
G1 X21.5875 Y-38.4124 Z-1.5875 F1016.0000
G1 X38.4124 Y-38.4124 Z-3.1750
; cut
G1 X21.5875 Y-38.4124 F1016
G1 X21.5875 Y-21.5875
G1 X38.4124 Y-21.5875
G1 X38.4124 Y-38.4124
; Retract
G1 Z2.5400 F2540
M2