import cv2 as cv
import numpy as np
import glob
from constants import *
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom


# Allows us to iterate over each camera
cams = glob.glob("../data/*/")

# termination criteria for findchessboard
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)


def writeToXML(filepath, camera_matrix, distortion_coeffs):
    # Create XML structure
    root = ET.Element("opencv_storage")

    # CameraMatrix
    camera_matrix_elem = ET.SubElement(root, "CameraMatrix", type_id="opencv-matrix")
    ET.SubElement(camera_matrix_elem, "rows").text = str(camera_matrix.shape[0])
    ET.SubElement(camera_matrix_elem, "cols").text = str(camera_matrix.shape[1])
    ET.SubElement(camera_matrix_elem, "dt").text = "f"
    data_elem = ET.SubElement(camera_matrix_elem, "data")
    data_elem.text = "\n".join(" ".join(map(str, row)) for row in camera_matrix)

    # DistortionCoeffs
    distortion_coeffs_elem = ET.SubElement(root, "DistortionCoeffs", type_id="opencv-matrix")
    ET.SubElement(distortion_coeffs_elem, "rows").text = str(distortion_coeffs.shape[0])
    ET.SubElement(distortion_coeffs_elem, "cols").text = str(distortion_coeffs.shape[1])
    ET.SubElement(distortion_coeffs_elem, "dt").text = "f"
    data_elem = ET.SubElement(distortion_coeffs_elem, "data")
    data_elem.text = "\n".join(map(str, distortion_coeffs[0]))

    # Write to XML file
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")

    # Write to XML file
    with open(filepath, "w") as f:
        f.write(xml_str)


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

        ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, grey.shape[::-1], None, None)

        writeToXML(cam + "intrinsics.xml", mtx, dist)
        print(f"Intrinsics written to {cam}intrinsics.xml\n")
