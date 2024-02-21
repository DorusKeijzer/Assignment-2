import cv2 as cv
import numpy as np
import glob
from constants import *

AXIS = np.float32([[3,0,0], [0,3,0], [0,0,-3], [1,0,0],[0,1,0],[0,0,-1],[0,0,0 ],  [1,1,0], [0,0,0],[0,0,0],[1,1,0], [1,1,0],[0,0,-1],[1,1,-1], [1,1,-1],
                       [1,0,-1],[0,1,-1],[0,1,-1],[0,0,-1],[1,1,-1],[0,1,0],[1,0,0], [0,1,0], [1,0,0],[1,0,-1], [0,1,-1], [1,0,-1]])
AXIS = AXIS * SQUARESIZE

# Allows us to iterate over each camera
cams = glob.glob("../data/*/")
cv.namedWindow('image')

def drawcube(img, corners, imgpts):
    imgpts = np.int32(imgpts).reshape(-1,2)
    # draw pillars in blue color
    for i,j in zip(range(12),range(12,24)):
        img = cv.line(img, tuple(imgpts[i]), tuple(imgpts[j]),(66, 245, 236),1)
    return img

def drawaxes(img, corners, imgpts):
    # Extracting corner coordinates properly
    corner = tuple(corners[0].ravel())
    corner = tuple(map(int, corner))
    # Extracting imgpts coordinates properly
    imgpts = np.int32(imgpts).reshape(-1, 2)
    imgpts = imgpts.astype(int)  # Convert imgpts to Python integers
    
    # Drawing lines from corner to imgpts        
    img = cv.line(img, corner, tuple(imgpts[0]), (255, 0, 0), 2)
    img = cv.line(img, corner, tuple(imgpts[1]), (0, 255, 0), 2)
    img = cv.line(img, corner, tuple(imgpts[2]), (0, 0, 255), 2)

    return img

def readConfig(camera_path):
    """Reads configs.xml and gives the camera parameters"""
    fs = cv.FileStorage(camera_path+"configs.xml", cv.FILE_STORAGE_READ)
    camera_matrix = fs.getNode("CameraMatrix").mat()
    dist_coeffs = fs.getNode("DistortionCoeffs").mat()
    rvec = fs.getNode("Rvec").mat()
    tvec = fs.getNode("Tvec").mat()
    corners = fs.getNode("Corners").mat()
    fs.release()
    return camera_matrix, dist_coeffs, rvec, tvec, corners

if __name__ == "__main__":
    for cam in cams:
        # reads the xml file corresponding to this camera
        cameraMatrix, distCoeffs, rvec, tvec, corners = readConfig(cam)

        # open the checkerboard video file for this camera in order to draw the cube
        calibration_video_path = cam + "checkerboard.avi"
        print(f"Reading {calibration_video_path}" )
        cap = cv.VideoCapture(calibration_video_path)

        # Check if the video file was successfully opened
        if not cap.isOpened():
            print("Error: Could not open the video file.")
            exit()

        ret, frame = cap.read()
        imgpts, _ = cv.projectPoints(AXIS, rvec, tvec, cameraMatrix, distCoeffs )
        # draw the cube and the axes
        frame = drawaxes(frame, corners, imgpts[0:3])
        frame = drawcube(frame, corners, imgpts[3:])

        cv.imshow("image", frame)
        cv.waitKey(500)

        cap.release()
