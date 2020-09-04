import robot_motion as rm
from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2
import os
import time
import pickle

if(__name__=="__main__"):
    motionsystem = rm.colonyPicker({},{},'/dev/serial0',19200)
    img_folder = "pictures"

    
    pickfle = open("camera_matrix.pckl","rb")
    mtx,dist = pickle.load(pickfle)

    camera = PiCamera()
    camera.resolution = '1920x1088'
    camera.shutter_speed = 2000
    rawCapture = PiRGBArray(camera)
    plates = {"A1":"first_plate","A2":"second_plate","A3":"third_plate","B1":"fifth"}
    plate_order = {"C":[3,2,1],"B":[3,2,1],"A":[3,2,1]}
    staging_floors = sorted(list(motionsystem.robopos["plate_staging"].keys()))

    plates_stored = []
    for stack in plate_order:
        staging_floors = sorted(list(motionsystem.robopos["plate_staging"].keys()))
        for plate_num in plate_order[stack]:
            plateloc = stack+str(plate_num)
            if(plateloc in plates):
                impath = os.path.join(".",img_folder,plateloc+".png")
                impath_calib = os.path.join(".",img_folder,plateloc+"_calibrated.png")
                motionsystem.get_plate(plateloc)
                motionsystem.put_plate("0","plate_backlight","up")
                motionsystem.grab_lid()
                motionsystem.move_robot(pz = 65)
                motionsystem.move_robot(px=motionsystem.robopos["neutral_position"]["0"]["X"])
                motionsystem.light_on(.7)
                motionsystem.send_gcode_multiline(["M400"])
                #capture the image using the camera
                camera.capture(rawCapture,format="bgr")
                img = rawCapture.array
                cv2.imwrite(impath,img)
                #undistort the image
                h,  w = img.shape[:2]
                newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
                dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
                x,y,w,h = roi
                dst = dst[y:y+h, x:x+w]
                
                cv2.imwrite(impath_calib,dst)

                motionsystem.light_off()
                motionsystem.place_lid()
                motionsystem.get_plate("0","plate_backlight","up")
                motionsystem.put_plate(staging_floors[0],"plate_staging")
                plates_stored.append([staging_floors[0],plateloc])
                staging_floors = staging_floors[1:]
        for plate_stored in plates_stored[::-1]:
            motionsystem.get_plate(plate_stored[0],"plate_staging")
            motionsystem.put_plate(plate_stored[1])
        #TODO reset plates stored every stack
        plates_stored = []
