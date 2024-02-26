import cv2 as cv
from constants import *
import glob
import numpy as np
import assignment
from utils import readXML, debugMatrices

class camera:
    """Stores the properties of a camera
        path: path to the camera folder
        matrix: camera matrix
        distcoeffs: distortion coefficients
        rvec: rotation vector
        tvec: translation vector
        table: lookup table between image points and voxels
        voxelgrid: the voxels that are on or off from this cameras perspective"""
    matrix, distcoeffs, rvec, tvec, table, voxelgrid = ..., ..., ... , ..., ..., ...
    
    def __init__(self, path):
        self.path = path
        self.matrix, self.distcoeffs, self.rvec, self.tvec = readXML(path+"configs.xml", "CameraMatrix", "DistortionCoeffs", "Rvec", "Tvec")
        
    def initializeTable(self, voxelgrid):
        """Sets up the lookup table"""
        self.table = table()
        self.table.populateTable(voxelgrid, self)

    def populateVoxelgrid(self, image):
        for pixel in image:
            voxel = self.table[pixel] 
            if pixel.isOn():
                voxel.value = True

class voxelgrid:
    def __init__(self,x,y,z):
        self.grid = np.zeros((x,y,z))
        self.shape = self.grid.shape
    
    def __str__(self):
        return str(self.grid)
    




class lookuptableData:
    """Format for the data inside the lookup table"""
    voxel_coords, image_coords = ..., ...

    def __init__(self, voxel_coords, image_coords):
        self.voxel_coords = voxel_coords
        self.image_coords = image_coords

class table:
    """A lookup table mapping voxels to image pixels for a given camera"""
    table = ...
    def __init__(self):
        self.table = []

    def add(self, item):
        self.table.append(item)

    def populateTable(self, voxels, cam: camera):
        """Projects every voxel onto image pixels"""
        # iterates over voxels
        for x in range(voxels.shape[0]):
            for y in range(voxels.shape[1]):
                for z in range(voxels.shape[2]):

                    # projects the voxel at x, y, z to 2d image coordinates and add to lookup
                    x_img, y_img = project(np.array([x,y,z]), cam)

                    self.add(lookuptableData(voxels.grid[x,y,z], (x_img, y_img)))
    
def project(voxel, cam: camera):
    """Projects a 3D voxel onto the 2D image of the specified camera"""
    debugMatrices(voxel, cam.rvec, cam.tvec, cam.matrix, cam.distcoeffs)
    imagepoints, _ = cv.projectPoints(voxel, cam.rvec, cam.tvec, cam.matrix, cam.distcoeffs)
    return imagepoints

class MyIterator:
    def __init__(self, data):
        self.data = data
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.data):
            item = self.data[self.index]
            self.index += 1
            return item
        else:
            raise StopIteration

def isForeGround(pixel):
    raise NotImplementedError

if __name__ == "__main__":
    camera_paths = glob.glob("data/*/")
    cameras = []
    for camera_path in camera_paths:
        cameras.append(camera(camera_path))
    
    for cam in cameras:
        voxelgrid = voxelgrid(128, 128, 128)
        cam.initializeTable(voxelgrid)
        subtracted_video = cam.path + "subtracted"
        cap = cv.VideoCapture("Video", subtracted_video)
        cap.release()
        # cam.populateVoxelgrid(image)

