import robot_motion as rm
try:
    import robot_camera
    picam_exists = True
except ModuleNotFoundError:
    print("no picamera!")
    picam_exists=False
import os
import time
import csv
import copy
def load_platefile(platefilename):
    platedict = {}
    with open(platefilename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        colnames = []
        for row in csv_reader:
            if line_count == 0:
                colnames = row
            else:
                keyval = None
                for val,colname in zip(row,colnames):
                    if(colname== "position"):
                        keyval = val
                    elif(keyval is not None):
                        platedict[keyval] = val
            line_count+=1
    return platedict

if(__name__=="__main__"):
    motionsystem = rm.colonyPicker({},{},'/dev/serial0',19200)
    robocam = robot_camera.robo_camera()
    img_folder = "pictures"
    plates = load_platefile("plates_to_use.csv")

    plates_stored = []
    for stack in motionsystem.plate_order:
        staging_floors = copy.deepcopy(motionsystem.staging_floors)
        for plate_num in motionsystem.plate_order[stack]:
            plateloc = stack+str(plate_num)
            if(plateloc in plates):
                impath_calib = os.path.join(".",img_folder,plateloc+"_calibrated.png")
                motionsystem.get_plate(plateloc)
                motionsystem.put_plate("0","plate_backlight","up")
                motionsystem.grab_lid()
                #go up after grabbing the lid to avoid the induction heater
                motionsystem.move_robot(pz = 65)
                #move back so the camera can see the plate
                motionsystem.move_robot(px=motionsystem.robopos["neutral_position"]["0"]["X"])
                motionsystem.light_on(.7) #lights on
                motionsystem.send_gcode_multiline(["M400"]) #wait for movement before the next part
                platepic = robocam.capture(savepath=impath_calib) #take a picture
                motionsystem.light_off() #done taking a picture so light off
                motionsystem.place_lid() #replace the lid
                motionsystem.get_plate("0","plate_backlight","up") #pick up the plate
                motionsystem.put_plate(staging_floors[0],"plate_staging") #store it in the right place
                plates_stored.append([staging_floors[0],plateloc])
                staging_floors = staging_floors[1:]
        for plate_stored in plates_stored[::-1]:
            motionsystem.get_plate(plate_stored[0],"plate_staging")
            motionsystem.put_plate(plate_stored[1])
        plates_stored = []
