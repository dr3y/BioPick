import robot_motion as rm
from picamera import PiCamera
import os
import time

if(__name__=="__main__"):
    x = rm.colonyPicker({},{},'/dev/serial0',19200)
    img_folder = "pictures"
    camera = PiCamera()
    camera.resolution = '1920x1080'
    camera.shutter_speed = 2000
    plates = {"A1":"first_plate","A2":"second_plate","A3":"third_plate","B2":"fourth","B1":"fifth"}
    plate_order = {"C":[3,2,1],"B":[3,2,1],"A":[3,2,1]}
    staging_floors = sorted(list(x.robopos["plate_staging"].keys()))

    plates_stored = []
    for stack in plate_order:
        for plate_num in stack:
            plateloc = stack+str(plate_num)
            if(plateloc in plates):
                impath = os.path.join(".",img_folder,plateloc+".png")
                x.get_plate(plateloc)
                x.put_plate("0","plate_backlight","up")
                x.grab_lid()
                x.move_robot(px=x.robopos["neutral_position"]["0"]["X"])
                x.light_on(.7)
                x.send_gcode_multiline(["M400"])
                camera.capture(impath)
                x.light_off()
                x.place_lid()
                x.get_plate("0","plate_backlight","up")
                x.put_plate(staging_floors[0],"plate_staging")
                plates_stored.append([staging_floors[0],plateloc])
                staging_floors = staging_floors[1:]
        for plate_stored in plates_stored[::-1]:
            x.get_plate(plate_stored[0],"plate_staging")
            x.put_plate(plate_stored[1])
        plates_stored = []
