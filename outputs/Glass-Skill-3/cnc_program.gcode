; Glass-Skill-3 CNC Cutting Program
; Generated: 2026-01-15
; Material: Clear Tempered Glass, 4.0mm thick
; Units: mm

; ==========================================
; PANEL 1 - RECTANGLE (1035 x 2835 mm)
; ==========================================

; Move to start position
G00 X0 Y0 Z5
M03 S10000 ; Start spindle

; Cut Panel 1 outline
G01 Z-4.5 F500 ; Plunge
G01 X1035 Y0 F1000 ; Bottom edge
G01 X1035 Y2835 ; Right edge
G01 X0 Y2835 ; Top edge
G01 X0 Y0 ; Left edge (close)

G00 Z5 ; Retract

; Panel 1 Holes (4x)
; Hole 1 - Bottom Left (30, 30)
G00 X30 Y30
G01 Z-4.5 F300
G02 X30 Y30 I5 J0 ; Circle cut, radius 5mm
G00 Z5

; Hole 2 - Bottom Right (1005, 30)
G00 X1005 Y30
G01 Z-4.5 F300
G02 X1005 Y30 I5 J0
G00 Z5

; Hole 3 - Top Left (30, 2805)
G00 X30 Y2805
G01 Z-4.5 F300
G02 X30 Y2805 I5 J0
G00 Z5

; Hole 4 - Top Right (1005, 2805)
G00 X1005 Y2805
G01 Z-4.5 F300
G02 X1005 Y2805 I5 J0
G00 Z5

; ==========================================
; PANEL 2 - L-SHAPED (997 x 2840 mm)
; ==========================================

; Move to Panel 2 start (offset by 1050mm for separation)
G00 X1050 Y0 Z5

; Cut Panel 2 L-Shape outline
; Starting from bottom-left corner
G01 Z-4.5 F500
G01 X2043 Y0 F1000 ; Bottom edge (1050 + 993 = 2043)
G01 X2043 Y2130 ; Right edge up to step
G01 X2047 Y2130 ; Step horizontal (993 to 997 = 4mm)
G01 X2047 Y2840 ; Right edge to top
G01 X1050 Y2840 ; Top edge
G01 X1050 Y0 ; Left edge (close)

G00 Z5 ; Retract

; Panel 2 Holes (4x on lower section)
; Hole 1 - Bottom Left (1050+30, 30)
G00 X1080 Y30
G01 Z-4.5 F300
G02 X1080 Y30 I5 J0
G00 Z5

; Hole 2 - Bottom Right (1050+963, 30)
G00 X2013 Y30
G01 Z-4.5 F300
G02 X2013 Y30 I5 J0
G00 Z5

; Hole 3 - Upper Left (1050+30, 2100)
G00 X1080 Y2100
G01 Z-4.5 F300
G02 X1080 Y2100 I5 J0
G00 Z5

; Hole 4 - Upper Right (1050+963, 2100)
G00 X2013 Y2100
G01 Z-4.5 F300
G02 X2013 Y2100 I5 J0
G00 Z5

; ==========================================
; END PROGRAM
; ==========================================

M05 ; Stop spindle
G00 X0 Y0 Z50 ; Return to home
M30 ; End program

; ==========================================
; NOTES:
; - Panel 1: Standard rectangle, 4 corner holes
; - Panel 2: L-shape with step at Y=2130mm
; - All holes: 10mm diameter (5mm radius)
; - K-edge finish required on all edges
; - Tolerance: +/- 1.5mm
; ==========================================
