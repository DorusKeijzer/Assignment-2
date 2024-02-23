import cv2 as cv
import numpy as np
import glob
from constants import *
import utils

# Allows us to iterate over each camera
cams = glob.glob("data/*/")
cv.namedWindow('image')


# stores the pixels coordinates of the clicks
clickcorners = []

def interpolate(corners, chessboardwidth, chessboardheight):
    """Expects:
       the pixel coordinates of the 4 corners of a chessboard in an np array of size 4
       the proportions of the chessboard, 

       returns where the internal crossings are as a np array of size (chessboardwidth x chessboard height) """

    # the coordinates of the outer corners of the chessboard in chessboard coordinates
    # these will be used to solve for the transformation matrix
    # manual coordinates need to be specified in the same order (Bottom right, bottom left, top right, top left)
    corner_chesscoordinates = np.float32([[0,0], 
                         [0,chessboardwidth-1], 
                         [chessboardheight-1, 0], 
                         [chessboardheight-1, chessboardwidth-1]])   
    
    # Finds the transformation matrix 
    TransformationMatrix = cv.getPerspectiveTransform(corner_chesscoordinates, corners)

    # The coordinates of the chessboard corners in chessboard coordinates (i.e. [[[0,0]],[[0,1]],[[0,2]],...
    #                                                                            [[1,1]],[[1,2]],[[1,3]],..)
    chessboard_coords = np.float32([[[x, y]] for x in range(chessboardheight) for y in range(chessboardwidth)])

    # applies the transformation
    inner_corners = cv.perspectiveTransform(chessboard_coords, TransformationMatrix)
    return inner_corners.reshape(-1, 2)

def click_event(event, x, y, flags, param): 
    """Temporarily stores the clicked pixel coordinates to the global variable'clickcorners'"""
    img = param
    if event == cv.EVENT_FLAG_LBUTTON:
        cv.circle(img, (x,y), 1, (0,0,255),-1)
        clickcorners.append([x,y])
        cv.imshow("image", img)

def manualCorners() -> np.array:
    """ALlows the user to specify the corners. 
    These corners should be given in the same order as the program does.
    returns an array of the correct size with the corner points
    
    Order of clicks is important. : 
    Bottom right, bottom left, top right, top left
    """
    
    # The mouse click event writes the corners to this variable, hence it's used here.
    global clickcorners    

    # Waits for the user to click 4 corners
    while(len(clickcorners)<4):
        cv.waitKey(3)
    
    # stores these corners in an np array 
    res = np.array(clickcorners, dtype=np.float32)

    clickcorners = []

    return res

# [0. 0.], [1. 0.], [2. 0.], [3. 0.], [4. 0.], ... [1,9], [1,1], etc.
objectpoints = np.mgrid[0:CHESSBOARDWIDTH,0:CHESSBOARDHEIGHT].T.reshape(-1,2)
objectpoints = objectpoints.astype(np.float32) 
objectpoints = np.hstack((objectpoints, np.zeros((objectpoints.shape[0], 1), dtype=np.float32))) # turns into 3d points with z = 0
objectpoints = SQUARESIZE * objectpoints # multiply with the size of the square

if __name__ == "__main__":
    for cam in cams:
        # reads the xml file corresponding to this camera
        cameraMatrix, distCoeffs = utils.readXML(cam + "intrinsics.xml", "CameraMatrix", "DistanceCoeffs")

        # open the checkerboard video file for this camera
        calibration_video_path = cam + "checkerboard.avi"
        print(f"Reading {calibration_video_path}" )
        cap = cv.VideoCapture(calibration_video_path)

        # Check if the video file was successfully opened
        if not cap.isOpened():
            print("Error: Could not open the video file.")
            exit()

        ret, frame = cap.read()
        cv.setMouseCallback('image', click_event, frame)
        cv.imshow("image", frame)
        
        print(f"Please manually specify the corner points for {calibration_video_path}")

        # makes the user specify the corner points and interpolates the inner points
        outercorners = manualCorners()
        innercorners = interpolate(outercorners, CHESSBOARDWIDTH, CHESSBOARDHEIGHT) 
        cv.drawChessboardCorners(frame, (CHESSBOARDWIDTH, CHESSBOARDHEIGHT), innercorners, True)
        cv.imshow("image", frame)
        cv.waitKey(500)

        ret, rvec, tvec = cv.solvePnP(objectpoints, innercorners, cameraMatrix, distCoeffs)

        # writes vectors to configs.xml
        fs = cv.FileStorage(cam+"configs.xml", cv.FILE_STORAGE_WRITE)

        fs.write("CameraMatrix", cameraMatrix)
        fs.write("DistortionCoeffs", distCoeffs)
        fs.write("Rvec", rvec)
        fs.write("Tvec", tvec)
        fs.write("Corners", innercorners)

        fs.release()
        print(f"Camera parameters written to {cam}configs.xml")

        cap.release()
