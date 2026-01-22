; ================================================================
; GLASS PANEL CNC DRILLING PROGRAM
; ================================================================
; Generated: 2026-01-15 20:52:00
; Generator: Glass Manufacturing Skill v1.0
; ================================================================
;
; PANEL SPECIFICATIONS:
; Width:     2920 mm
; Height:    975 mm
; Thickness: 4.0 mm
; Holes:     4
;
; MACHINE REQUIREMENTS:
; - Diamond core drill bits
; - Continuous water coolant system
; - Back support plate installed
; - Vacuum or clamp fixturing
;
; SAFETY NOTES:
; - Verify workpiece is securely fixtured
; - Check coolant flow before starting
; - Wear appropriate PPE
; - Do not leave machine unattended
;
; ================================================================

; --- PROGRAM START ---
%
O0001 (GLASS PANEL DRILLING)

; --- SAFETY BLOCK ---
G90 G94 G17 G40 G49 G80  ; Absolute, feed/min, XY plane, cancel comp/cycles
G21                       ; Metric units (mm)
G28 G91 Z0               ; Home Z axis first
G90                       ; Return to absolute

; --- SET WORK COORDINATES ---
G54                       ; Use work coordinate system 1
; Assumes origin at bottom-left corner of glass panel

; --- SPINDLE AND COOLANT ---
S3000 M3       ; Start spindle CW at 3000 RPM
G4 P2000                  ; Dwell 2 seconds for spindle to reach speed
M8              ; Coolant ON (water for glass drilling)

; --- RAPID TO SAFE HEIGHT ---
G0 Z10.0              ; Move to safe Z height


; ================================================================
; HOLE 1 of 4
; Position: X=908, Y=30
; Diameter: 8 mm
; ================================================================

; Rapid to position above hole
G0 X908.000 Y30.000      ; Move to hole center
G0 Z3.0             ; Rapid to approach height

; --- PECK DRILLING CYCLE ---
; Using G83 peck drilling for clean hole quality
G83 X908.000 Y30.000 Z-6.000 R3.0 Q1.5 F10
; G83: Peck drilling cycle
;   X,Y: Hole position
;   Z: Final depth (6.0mm through 4.0mm glass)
;   R: Retract plane (3.0mm)
;   Q: Peck increment (1.5mm)
;   F: Feed rate (10 mm/min)

G80                       ; Cancel canned cycle
G0 Z10.0              ; Retract to safe height

; Inspection pause (optional - remove for production)
; M0                      ; Optional stop for hole inspection

; ================================================================
; HOLE 2 of 4
; Position: X=1869, Y=30
; Diameter: 8 mm
; ================================================================

; Rapid to position above hole
G0 X1869.000 Y30.000      ; Move to hole center
G0 Z3.0             ; Rapid to approach height

; --- PECK DRILLING CYCLE ---
; Using G83 peck drilling for clean hole quality
G83 X1869.000 Y30.000 Z-6.000 R3.0 Q1.5 F10
; G83: Peck drilling cycle
;   X,Y: Hole position
;   Z: Final depth (6.0mm through 4.0mm glass)
;   R: Retract plane (3.0mm)
;   Q: Peck increment (1.5mm)
;   F: Feed rate (10 mm/min)

G80                       ; Cancel canned cycle
G0 Z10.0              ; Retract to safe height

; Inspection pause (optional - remove for production)
; M0                      ; Optional stop for hole inspection

; ================================================================
; HOLE 3 of 4
; Position: X=1929, Y=30
; Diameter: 8 mm
; ================================================================

; Rapid to position above hole
G0 X1929.000 Y30.000      ; Move to hole center
G0 Z3.0             ; Rapid to approach height

; --- PECK DRILLING CYCLE ---
; Using G83 peck drilling for clean hole quality
G83 X1929.000 Y30.000 Z-6.000 R3.0 Q1.5 F10
; G83: Peck drilling cycle
;   X,Y: Hole position
;   Z: Final depth (6.0mm through 4.0mm glass)
;   R: Retract plane (3.0mm)
;   Q: Peck increment (1.5mm)
;   F: Feed rate (10 mm/min)

G80                       ; Cancel canned cycle
G0 Z10.0              ; Retract to safe height

; Inspection pause (optional - remove for production)
; M0                      ; Optional stop for hole inspection

; ================================================================
; HOLE 4 of 4
; Position: X=2890, Y=30
; Diameter: 8 mm
; ================================================================

; Rapid to position above hole
G0 X2890.000 Y30.000      ; Move to hole center
G0 Z3.0             ; Rapid to approach height

; --- PECK DRILLING CYCLE ---
; Using G83 peck drilling for clean hole quality
G83 X2890.000 Y30.000 Z-6.000 R3.0 Q1.5 F10
; G83: Peck drilling cycle
;   X,Y: Hole position
;   Z: Final depth (6.0mm through 4.0mm glass)
;   R: Retract plane (3.0mm)
;   Q: Peck increment (1.5mm)
;   F: Feed rate (10 mm/min)

G80                       ; Cancel canned cycle
G0 Z10.0              ; Retract to safe height

; Inspection pause (optional - remove for production)
; M0                      ; Optional stop for hole inspection

; ================================================================
; PROGRAM END
; ================================================================

; --- RETURN TO HOME ---
M9             ; Coolant OFF
G0 Z10.0              ; Ensure safe Z height
M5                        ; Spindle STOP
G28 G91 Z0               ; Home Z axis
G28 X0 Y0                ; Home X and Y axes
G90                       ; Absolute mode

; --- PROGRAM COMPLETE ---
M30                       ; End program and rewind

%

; ================================================================
; POST-PROCESSING NOTES:
; ================================================================
; 1. Inspect all holes for chips or cracks
; 2. Deburr hole edges if necessary
; 3. Clean glass surface of coolant residue
; 4. Verify hole positions with gauge
; 5. Document any deviations
; ================================================================
