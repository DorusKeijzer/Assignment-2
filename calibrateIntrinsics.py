import cv2 as cv
import numpy as np
import glob
from constants import *

# Allows us to iterate over each camera
cams = glob.glob("data/*/")

# termination criteria for findchessboard
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

if __name__ == "__main__":

    for cam in cams:
        # Stores the corner points.
        objp = np.zeros((CHESSBOARDWIDTH*CHESSBOARDHEIGHT,3), np.float32)
        objp[:,:2] = SQUARESIZE * np.mgrid[0:CHESSBOARDWIDTH,0:CHESSBOARDHEIGHT].T.reshape(-1,2)

        # Arrays to store object points and image points from all the images.
        objpoints = [] # 3d point in real world space
        imgpoints = [] # 2d points in image plane.

        # open the video file for this camera
        calibration_video_path = cam + "intrinsics.avi"
        print(f"Reading {calibration_video_path}" )
        cap = cv.VideoCapture(calibration_video_path)

        # Check if the video file was successfully opened
        if not cap.isOpened():
            print("Error: Could not open the video file.")
            exit()

        frame_number = 0
        # Read and display frames from the video file
        while True:
            frame_number += 1
            # Read a frame
            ret, frame = cap.read()
            # If the frame is not read correctly, break the loop
            # this terminates the loop after the last frame
            if not ret:
                break
            
            # every 100 frames
            if frame_number % 100 == 0:
                grey = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

                # Find the chess board corners
                ret, corners = cv.findChessboardCorners(grey, (CHESSBOARDWIDTH,CHESSBOARDHEIGHT), None) 
                if ret: # the built in function succeeds
                    corners = cv.cornerSubPix(grey, corners, (11,11), (-1,-1), criteria)
                    objpoints.append(objp)
                    imgpoints.append(corners)


        # Release the VideoCapture object 
        cap.release()

        ret, mtx, dist, _, _ = cv.calibrateCamera(objpoints, imgpoints, grey.shape[::-1], None, None)
        
        fs = cv.FileStorage(cam+"intrinsics.xml", cv.FILE_STORAGE_WRITE)
        fs.write("CameraMatrix", mtx)
        fs.write("DistortionCoeffs", dist)

        fs.release()


        print(f"Intrinsics written to {cam}intrinsics.xml")
