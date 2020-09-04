import numpy as np
import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray
import pickle
import glob
import os

class robo_camera:
    def __init__(self,resolution="1920x1080",shutter_speed=2000,camera_matrix="camera_matrix.pckl"):
        self.mtx = None
        self.dist = None
        self.cam_calibrated = False
        if(camera_matrix is not None):
            pickfle = open(camera_matrix,"rb")
            mtx,dist = pickle.load(pickfle)
            self.mtx = mtx
            self.dist = dist
            self.cam_calibrated = True
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.shutter_speed = 2000
    def capture(self,savepath=None):
        rawCapture = PiRGBArray(self.camera)
        self.camera.capture(rawCapture,format="bgr")
        img = rawCapture.array
        if(self.cam_calibrated):
            #undistort the camera if it is calibrated
            h,  w = img.shape[:2]
            newcameramtx, roi=cv2.getOptimalNewCameraMatrix(self.mtx,self.dist,\
                                                                (w,h),1,(w,h))
            dst = cv2.undistort(img, self.mtx, self.dist, None, newcameramtx)
            x,y,w,h = roi
            dst = dst[y:y+h, x:x+w]
            img = dst
        if(savepath is not None):
            #save it if that is desired
            cv2.imwrite(savepath,img)
        return img
        
