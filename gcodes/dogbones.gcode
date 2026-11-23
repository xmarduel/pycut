G21         ; Set units to mm
G90         ; Absolute positioning
G1 Z10.0000    F1000      ; Move to clearance level

; Start the spindle
M3 S10000

;
; Tool Info
; Diameter:    3.0


;
; Operation:    1
; Name:         op
; Type:         Inside
; Paths:        1
; Direction:    Conventional
; Cut Depth:    5.0
; Pass Depth:   1.0
; Plunge rate:  127
; Cut rate:     1000
;
;

; Path 1
; Rapid to initial position
G1 X-24.250 Y24.250 F1000
G1 Z0.000
; plunge
G1 Z-1.000 F127
; cut
G1 X24.250 Y24.250  F1000

; fix up begin ------------------------
G91
G1 X0.4393 Y0.4393 ( goes 0.8786 mm top right )
G1 X-0.4393 Y-0.4393  ( and back )
G90
; fix up end --------------------------

G1 X24.250 Y-24.250
; Retract to Clearance
G1 Z10.000 F1000
; Rapid to initial position
G1 X-24.250 Y24.250 F1000
G1 Z-1.000
; plunge
G1 Z-2.000 F127
; cut
G1 X24.250 Y24.250  F1000
G1 X24.250 Y-24.250
; Retract to Clearance
G1 Z10.000 F1000
; Rapid to initial position
G1 X-24.250 Y24.250 F1000
G1 Z-2.000
; plunge
G1 Z-3.000 F127
; cut
G1 X24.250 Y24.250  F1000
G1 X24.250 Y-24.250
; Retract to Clearance
G1 Z10.000 F1000
; Rapid to initial position
G1 X-24.250 Y24.250 F1000
G1 Z-3.000
; plunge
G1 Z-4.000 F127
; cut
G1 X24.250 Y24.250  F1000
G1 X24.250 Y-24.250
; Retract to Clearance
G1 Z10.000 F1000
; Rapid to initial position
G1 X-24.250 Y24.250 F1000
G1 Z-4.000
; plunge
G1 Z-5.000 F127
; cut
G1 X24.250 Y24.250  F1000
G1 X24.250 Y-24.250
; Retract to Clearance
G1 Z10.000 F1000
; Rapid to initial position
G1 X-24.250 Y24.250 F1000

; Stop the spindle
M5

; Return to 0,0
G0 X0 Y0 F1000

; Program End
M2
