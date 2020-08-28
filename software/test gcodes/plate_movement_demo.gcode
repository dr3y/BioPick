G28 Z0 ;home z
M400 ;finish moves
M280 P1 S55 ;open gripper
M280 P1 S30 ;close gripper
M280 P0 S35 ;turn lid up
G4 P500 ;wait half a second
M280 P0 S150 ;turn lid down
G4 P500 ;wait half a second
G28 Y0 E0;home y
G1 Y180 F2500 ;back off from y max
M400
M280 P1 S55 ;open gripper
G28 X0 ;home x



;pickup plate A2
G1 Z65 F2500 ;go up
G1 X81.2 Y20.9 F2500 ;over the top of A stack
G1 Z15.25 F2500 ;down to the right height
M400 ;finish
M280 P1 S30 ;grip
G4 P500 ;wait half a second
G1 Z25.25 F2500 ;go up a bit

;place on staging area
G1 X159.2 F2500
G1 Y20.9 F2500
G1 Z1.75 F1300
M400
M280 P1 S55 ;open gripper
G4 P500 ;wait half a second
G1 Z65 F2500 ;go up

;pick up the bottom plate
G1 X81.2 Y20.9 F2500 ;over the top of A stack
G1 Z1.75 F1000 ;down
M400 ;finish
M280 P1 S30 ;grip
G4 P500 ;wait half a second
G1 Z65 F2500 ;go up

;move to backlight
G1 X159 F2500 ;move to the right
G1 Y186.5 F2500 ;move back
G1 Z33 F2500 ;move down to plate flipping height
M400
G1 E2.5 F400 ;rotate the culture plate to the right
M280 P0 S35 ;flip plate lid up
G4 P500 ;wait half a second
G1 Z65 F2500 ;go back up
G1 X361.7 F2500 ;move over
G1 Z11.35 ;place plate down
M400
M280 P1 S55 ;open gripper
G4 P500 ;wait half a second

;pick up the lid
G1 Z18.85 F2500 ;lid grip height
M400
M280 P1 S35 ;grip the lid
G4 P500 ;wait half a second
G1 Z65 F2500 ;go up
G1 X330 F2500 ;move back
M106 S150 ;turn light on
G4 P3000 ;wait a second to simulate taking a picture
M107 ;turn light off
;sterilize needle
G1 Z65 F2500 ;go up
G1 X334 Y190 ;over the top of the coil
G1 Z51.75 ;down into the coil
G4 P1000 ;wait a second to simulate sterilizing
G1 Z65 F2500 ;go up

;simulate picking
G1 E-2.5 F400 ;rotate the plate to the left
G1 X264 Y170 F2500 ;hover over the stab
G1 Z10.5 ;stab
G1 Z65 ;go up
G1 X307 Y90 F2500 ;hover over A1
G1 Z20 F2500 ;stab A1
G1 Z65 F2500 ;go back up
G1 X159 Y186 F2500 ;back away
G1 E2.5 F400 ;rotate the plate back to the right

;replace the lid
G1 X361.7 Y185.3 F2500 ;hover over the plate
G1 Z20 F2500 ;go down but not into the plate
G1 Z18.85 F500 ;slowly put on the lid
M400 ;finish
M280 P1 S55 ;open gripper
G4 P500 ;wait half a second

;pick up the plate
G1 Z11.35 ;go to the bottom of the plate
M400
M280 P1 S30 ;grip
G4 P500 ;wait half a second
G28 Z0 ;go up and also home Z0
G1 X160 F2500 ;back out of the backlight area
G1 Z33 F2500 ;go to plate flip height
M400
M280 P0 S150 ;flip plate lid down
G4 P1000 ;wait 1 second
G1 Z65 F2500 ;go back up
G1 X81.2 Y20.9 F2500 ;move over the top of stack A
G1 Z8 F2500 ;move down fast but not all the way
G1 Z1.75 F400 ;slowly move the last bit, a bit lower than normal
M400
M280 P1 S55 ;open gripper
G4 P500 ;wait half a second
G1 Z65 F2500 ;go up
G1 X159.2 Y20.9 F2500 ;hover over the staging area
G1 Z1.75 F2500 ;go down
M400
M280 P1 S30 ;grip
G4 P500
G1 Z65 F2500
G1 X81.2 Y20.9 F2500 ;over the top of stack A
G1 Z19 F2500 ;go down almost to the right spot
G1 Z15.25 F400 ;slower the last bit
M400
M280 P1 S55 ;ungrip
G4 P500
G28 Z0
G1 X159.2 Y20.9 F2500




