import cv2 as cv
from constants import *
import glob
import numpy as np
import assignment

def readXML(path, *args):
    """Imports the specified variables from the xml file at path"""
    fs = cv.FileStorage(path, cv.FILE_STORAGE_READ)
    res = []
    for arg in args:
        try:
            res.append(fs.getNode(arg).mat())
        except:
            pass
    fs.release()
    return res

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
        self.matrix, self.distcoeffs, self.rvec, self.tvec = readXML(path+"configs.xml", "CameraMatrix", "DistanceCoeffs", "Rvec", "Tvec")
        
    def initializeTable(self, voxelgrid):
        """Sets up the lookup table"""
        self.table = table()
        self.table.populateTable(voxelgrid, self)

    def populateVoxelgrid(self, image):
        for pixel in image:
            voxel = self.table[pixel] 
            if pixel.isOn():
                voxel.value = True

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
        for voxel in voxels:
            x_img, y_img = project(voxel, cam)
            self.add(lookuptableData(voxel, (x_img, y_img)))
    
def project(voxel, cam: camera):
    """Projects a 3D voxel onto the 2D image of the specified camera"""
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
    image = np.zeros((1028,1028))
    camera_paths = glob.glob("../data/*/")
    cameras = []
    for camera_path in camera_paths:
        cameras.append(camera(camera_path))
    
    for cam in cameras:
        cam.initializeTable()
        cam.populateVoxelgrid(image)
