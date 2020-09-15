import numpy as np
import cv2
try:
    from picamera import PiCamera
    from picamera.array import PiRGBArray
    CAMERA_ACTIVE = True
except ModuleNotFoundError:
    CAMERA_ACTIVE = False
import pickle
import glob
import os
from IPython.display import Image

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
        if(CAMERA_ACTIVE):
            self.camera = PiCamera()
            self.camera.resolution = resolution
            self.camera.shutter_speed = 2000
    def capture(self,savepath=None):
        if(not CAMERA_ACTIVE):
            return None
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
    def mask_lit_background(self,bg_image = None):
        if(bg_image is None):
            bg_image = self.capture()
        bgimg_gray = cv2.cvtColor(bg_image,cv2.COLOR_BGR2GRAY)
        bg_subtractor = cv2.createBackgroundSubtractorMOG2()
        fgmask = bg_subtractor.apply(bgimg_gray) #the first image is the background

        #kernel = np.ones((5,5), np.uint8) 
        kernel = np.array([[0, 1, 1, 1, 0],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [0, 1, 1, 1, 0]], dtype=np.uint8)

        ret,thresh = cv2.threshold(bgimg_gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) 
        thresh = cv2.erode(thresh,kernel,iterations=1) #get rid of noise
        thresh = cv2.dilate(thresh,kernel,iterations=2) #fill up the holes
        thresh = cv2.erode(thresh,kernel,iterations=10) #make it smaller
        return thresh, bg_subtractor
    def detect_needle(self,bg_image=None,thresh=None,bg_subtractor=None,needle_image=None):
        """detects a needle on top of a lit backdrop"""
        #setup background subtraction
        kernel = np.ones((3,3), np.uint8) 
        if(bg_image is None):
            assert((thresh is not None) and (bg_subtractor is not None))
        else:
            thresh,bg_subtractor = self.mask_lit_background(bg_image)
        #now the mask which represents the table is called "thresh"
        if(needle_image is None):
            needle_image = self.capture()
        gray = cv2.cvtColor(needle_image,cv2.COLOR_BGR2GRAY)
        bgmask = bg_subtractor.apply(gray,learningRate=0) #learningrate 0 means another image never becomes the new background
        bgmask = cv2.erode(bgmask,kernel,iterations=1) #erode a bit to get rid of junk
        #bgmask = cv2.dilate(bgmask,kernel,iterations=1) #erode a bit to get rid of junk

        ret,binary_needlepic = cv2.threshold(bgmask,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

        contours,_= cv2.findContours(binary_needlepic, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        biggest_contour = np.zeros((binary_needlepic.shape[0],binary_needlepic.shape[1],1),np.uint8)
        newcontours = []
        area_thresh = 100
        for contour in contours:
            carea = cv2.contourArea(contour)
            if(carea > area_thresh):
                newcontours += [contour]
        cv2.drawContours(biggest_contour, newcontours, -1, (255, 255, 255), -1)
        
        result = cv2.bitwise_and(thresh,biggest_contour)
        corners = cv2.goodFeaturesToTrack(biggest_contour, 1, .1, 10,mask=thresh,useHarrisDetector=True)
        corners = np.int0(corners)
        assert(len(corners[0])==1)
        return corners[0][0]
        
