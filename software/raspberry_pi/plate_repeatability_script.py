import robot_motion as rm
from picamera import PiCamera
import os
import time

if(__name__=="__main__"):
    x = rm.colonyPicker({},{},'/dev/serial0',19200)
    img_folder = "pictures"
    camera = PiCamera()
    plates = {"A1":"first_plate","A2":"second_plate","A3":"third_plate"}
    plate_order = ["C3","C2","C1","B3","B2","B1","A3","A2","A1"]
    staging_floors = sorted(list(x.robopos["plate_staging"].keys()))

    plates_stored = []
    for plateloc in plate_order:
        if(plateloc in plates):
            impath = os.path.join(".",img_folder,plateloc+".png")
            x.get_plate(plateloc)
            x.put_plate("0","plate_backlight","up")
            x.move_robot(px=x.robopos["neutral_position"]["0"]["X"])
            x.light_on()
            x.send_gcode_multiline(["M400"])
            camera.capture(impath)
            x.light_off()
            x.get_plate("0","plate_backlight","up")
            x.put_plate(staging_floors[0],"plate_staging")
            plates_stored.append([staging_floors[0],plateloc])
            staging_floors = staging_floors[1:]
    for plate_stored in plates_stored[::-1]:
        x.get_plate(plate_stored[0],"plate_staging")
        x.put_plate(plate_stored[1])
    plates_stored = []
