;first plate position
;X60 Y21 Z1.15
;backlight position
;X341.00 Y189.00 Z10.5
;A1 on culture plate position
;X295.00 Y76.00 Z58.00 E0 ;top
;X289.00 Y91.00 Z58.00 E-2.50 ;top
;sterilize position
;X317.00 Y189.00 Z:49



G28
G1 X460 Y370 F5000 ; move to a spot
M400
M280 P1 S70 ; fully open the gripper
M280 P0 S150 ;upside down
G4 P500 ;wait 0.5 sec
G1 Z142 ;bottom
M400
M280 P1 S40 ; barely open
M280 P1 S25 ; closed
G4 P500 ;wait 0.5 sec
G1 Z180 ; pickup the plate
M400
M280 P0 S35 ; rightside up
G4 P1000  ; wait 1 sec

G1 Z142 ;bottom
M400
M280 P1 S40 ; barely open
M280 P1 S50 ; fully open
G4 P500
G1 Z150 ;lid grip height
M400
M280 P1 S35 ; lid grip (if we are in upright rotation)
G4 P500
G1 Z180 ; pickup the lid
G4 P500
G1 Z150 ;lid grip height
M400
M280 P1 S50 ; fully open
G4 P500
G1 Z142 ;bottom
M400
M280 P1 S25 ; closed
G4 P500
G1 Z180 ; pickup the plate
M400
M280 P0 S150 ; upside down
G4 P1000
G1 Z142 ;bottom
M400
M280 P1 S40 ; barely open
M280 P1 S50 ; fully open
G4 P500
G1 Z195 ; go up
M400

;G1 Z150 ;lid grip height
;M280 P0 S150 ; upside down
;M280 P1 S40 ; barely open
;M280 P1 S25 ; closed
;M280 P1 S35 ; lid grip (if we are in upright rotation)