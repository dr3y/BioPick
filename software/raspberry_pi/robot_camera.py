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
import time
import peakutils.peak
from IPython.display import Image

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth
class robo_camera:
    def __init__(self,resolution="1920x1080",shutter_speed=2000,camera_matrix="camera_matrix.pckl"):
        self.mtx = None
        self.dist = None
        self.cam_calibrated = False
        if(camera_matrix is not None):
            pickfle = open(camera_matrix, "rb")
            mtx,dist = pickle.load(pickfle)
            self.mtx = mtx
            self.dist = dist
            self.cam_calibrated = True
        if(CAMERA_ACTIVE):
            self.camera = PiCamera()
            self.camera.resolution = resolution
            self.camera.shutter_speed = 2000
    def init_blob_detector(self,mint=130,maxt=500,mina=27,maxa=130,mincir=0.9,mincon=0.95,minin=.8):
        #################BLOB DETECTOR###############
        params = cv2.SimpleBlobDetector_Params()
        # Change thresholds
        params.minThreshold = mint
        params.maxThreshold = maxt

        # Filter by Area.
        params.filterByArea = True
        params.minArea = mina
        params.maxArea = maxa

        # Filter by Circularity
        params.filterByCircularity = True
        params.minCircularity = mincir

        # Filter by Convexity
        params.filterByConvexity = True
        params.minConvexity = mincon

        # Filter by Inertia
        params.filterByInertia = True
        params.minInertiaRatio = minin

        # Create a detector with the parameters
        detector = cv2.SimpleBlobDetector_create(params)
        return detector
    def detect_colonies(self,impath,image_transform,vector_transform,display_image=False,save_image=True,\
                                            mint=130,maxt=500,mina=27,maxa=130,mincir=0.9,mincon=0.95,minin=.8):
        img = cv2.imread(os.path.join('.','pictures',impath))
        x = time.localtime()
        tstamp = str(x.tm_year)[2:]+str(x.tm_mon)+str(x.tm_mday)+str(x.tm_hour)+str(x.tm_min)
        colonypick_path = os.path.join('.','pictures',str(tstamp+'_picked_'+impath))

        #this next part warps the image so that it is rectified and in the middle of the frame
        transform = image_transform
        warp = cv2.warpPerspective(img,transform,(500,550)) #transforming the calibrated image
        warp_gray = cv2.cvtColor(warp,cv2.COLOR_BGR2GRAY)
        #making a mask for colony finding
        warp_empty = np.zeros(shape=[550, 500, 1], dtype=np.uint8)
        center_coordinates = (230, 250) 
        axesLength = (170, 140) 
        warp_colony_mask = cv2.ellipse(warp_empty,center_coordinates,axesLength,0,0,360,255,-1)
        warp_gray_inv = 255-warp_gray
        warp_blur = cv2.GaussianBlur(warp_gray_inv,(101,101),50,borderType=cv2.BORDER_DEFAULT)
        #background subtraction
        colony_nobg = cv2.subtract(warp_gray_inv,warp_blur)
        colony_crop = (255-cv2.bitwise_and(colony_nobg, colony_nobg, mask=warp_colony_mask))*4
        #colony_crop = colony_crop.convertTo(colony_crop,cv2.CV_8U)
        maxval = np.max(colony_crop) #maximum pixel value in the image
        minval = np.min(colony_crop) #minimum pixel value in the image

        gaus = cv2.adaptiveThreshold(colony_crop, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 91, 12)
        
        gaus_eroded = cv2.dilate(gaus,np.ones([3,3]),iterations=1)
        gaus_eroded = cv2.erode(gaus_eroded,np.ones([3,3]),iterations=1)
        #gaus_eroded = gaus
        #cv2.imwrite('testimage.png',gaus_eroded)
        #display(Image('testimage.png'))


        detector = self.init_blob_detector(mint=mint,maxt=maxt,mina=mina,maxa=maxa,mincir=mincir,mincon=mincon,minin=minin)
        #blob detection
        keypoints = detector.detect(gaus_eroded)
        print(keypoints)
        #print(len(keypoints))        
        warp_with_keypoints = cv2.drawKeypoints(warp, keypoints,\
                        np.array([]), 255, cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        if(save_image):
            cv2.imwrite(colonypick_path, warp_with_keypoints)
            if(display_image):
                display(Image(filename=colonypick_path))
        elif(display_image):
            cv2.imwrite("testimage.png", warp_with_keypoints)
            display(Image(filename="testimage.png"))
        imstripe = warp[30:110, 215:235]
        imstripe_gray = cv2.cvtColor(imstripe, cv2.COLOR_BGR2GRAY)
        im_trace = np.mean(imstripe_gray, axis=1)
        im_deriv = smooth(-np.gradient(im_trace, 10), 4)
        #plt.figure()
        #plt.title(impath)
        im_base = peakutils.baseline(im_deriv, 2)
        im_deriv_debased = im_deriv-im_base
        #plt.plot(im_deriv_debased,label=impath)
        #plt.legend()

        highs = peakutils.peak.indexes(
            im_deriv_debased,
            thres=1/max(im_deriv_debased), min_dist=20
        )
        filteredhighs = []
        for high in highs:
            if(high >15 and high < 70):
                filteredhighs += [high]
        high_data = []
        for high in filteredhighs:
            yval = im_deriv_debased[high]
            high_data += [[yval,high]]
        #plt.plot([a[1] for a in high_data],[a[0] for a in high_data],'o')
        if(len(filteredhighs) != 2):
            agar_to_rim_distance = 34 #default assumption
        else:
            agar_to_rim_distance = filteredhighs[1]-filteredhighs[0]
        
        print("agar to rim distance is "+str(agar_to_rim_distance))
        return keypoints
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

        outputvalues = cv2.findContours(binary_needlepic, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #following is for compatibility with the raspberry pi version of opencv
        if(len(outputvalues)== 3):
            contours = outputvalues[1]
        elif(len(outputvalues)==2):
            contours = outputvalues[0]
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

    def needle_jog_calibration(self,bgimg_path,needlepath_dict):
        """performs the calibration that is required for rectifying an image given four pictures of the colony picking needle in different positions..
        bgimg_path: path to an image of the background with no needle
        needlepath_dict: a dictionary containing a needle image path as the key with the corresponding x,y,z coordinates as the value."""
        bgimg = cv2.imread(bgimg_path)
        
        thresh,bg_subtractor = self.mask_lit_background(bgimg)
        needlepoints = {}
        needle_positions = []
        for needle_image in needlepath_dict:
            needle_pos = tuple(needlepath_dict[needle_image])
            needle_positions += [needle_pos]
            img = cv2.imread(needle_image)
            npoint = self.detect_needle(thresh = thresh,\
                    bg_subtractor=bg_subtractor,needle_image=img)
            needlepoints[needle_pos]= npoint
        
        
        needle_xs = [a[0] for a in needle_positions]
        needle_ys = [a[1] for a in needle_positions]
        #needle_zs = [a[2] for a in needle_positions]
        sorted_positions = [
            (max(needle_xs),min(needle_ys)),
            (max(needle_xs),max(needle_ys)),
            (min(needle_xs),max(needle_ys)),
            (min(needle_xs),min(needle_ys)),
        ]
        sorted_needlepoint = []
        for sorted_pos in sorted_positions:
            sorted_needlepoint += [needlepoints[sorted_pos]]
        square = np.array([[0,200],[150,200],[150,50],[0,50]],np.float32)+150
        trapezoid = np.array(sorted_needlepoint,np.float32)
        transform = cv2.getPerspectiveTransform(trapezoid,square) #the transformation matrix




        square_2d = square[:2]
        #robo_x = rm.colonyPicker.load_posfile(posfilename="robot_positions.csv")["needle_pos"]["backlit_plate"]["X"]
        #robo_y = rm.colonyPicker.load_posfile(posfilename="robot_positions.csv")["needle_pos"]["backlit_plate"]["Y"]
        robot_square = np.array(needle_positions[:2],np.float32)
        #np.array([[10,-10],[10,10]],np.float32) #,[robo_x-10,robo_y+10],[robo_x-10,robo_y-10]
        tf_mtx = np.dot(np.linalg.inv(square_2d),robot_square)
        #robo_point = np.array([[robo_x,robo_y]],np.float32)

        return transform, tf_mtx

        
