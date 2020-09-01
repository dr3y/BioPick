def gcode_home(retchar = "\n"):
    homecode =[
        "G28 Z0 ;home z ",
        "M400 ;finish moves ",
        "M280 P1 S55 ;open gripper ",
        "M280 P1 S30 ;close gripper ",
        "M280 P0 S35 ;turn lid up ",
        "G4 P500 ;wait half a second ",
        "M280 P0 S150 ;turn lid down ",
        "G4 P500 ;wait half a second ",
        "G28 Y0 E0;home y ",
        "G1 Y180 F2500 ;back off from y max ",
        "M400 ",
        "M280 P1 S55 ;open gripper ",
        "G28 X0 ;home x ",
    ]
    retval = retchar.join(homecode)+retchar
    return homecode