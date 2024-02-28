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
    
    def __init__(self, path, voxelgrid):
        self.path = path
        self.matrix, self.distcoeffs, self.rvec, self.tvec = readXML(path+"configs.xml", "CameraMatrix", "DistortionCoeffs", "Rvec", "Tvec")
        self.voxelgrid = voxelgrid
    def initializeTable(self):
        """Sets up the lookup table"""
        self.table = table()
        self.table.populateTable(self.voxelgrid, self)

    def populateVoxelgrid(self, image):
        image = image[:,:,0]  # only takes one channel of the image
        print(image)
        for x in range(image.shape[0]):
            for y in range(image.shape[0]):
                pixel = image[x,y]
                # if the pixel in the imge is on
                if pixel != 0: 
                    # look up the voxels corresponding to this pixel 
                    voxel_ray = self.table.lookup((x,y))
                    print(voxel_ray)
                    for voxel in voxel_ray:
                        # set this voxel to one for this camera
                        self.voxelgrid[voxel] = 1

class voxelgrid:
    def __init__(self,x,y,z):
        self.grid = np.zeros((x,y,z))
        self.shape = self.grid.shape
    
    def __str__(self):
        return str(self.grid)
    
    
class table:
    """A lookup table mapping voxels to image pixels for a given camera"""
    table = ...
    def __init__(self):
        self.table = {}

    def __str__(self):
        res = ""
        for key, value in self.table.items():
            res += (f"{key}, {value}\n")
        return res
        # return ""

    def add(self, key, value):
        try:
            self.table[key].append(value)
        except:
            self.table[key] = [value]
    
    def lookup(self, key):
        try: 
            res = self.table[key] 
        except Exception as e:
            print(self)

    def populateTable(self, voxels, cam: camera):
        """Projects every voxel onto image pixels"""
        # iterates over voxels
        for x in range(voxels.shape[0]):
            for y in range(voxels.shape[1]):
                for z in range(voxels.shape[2]):
                    # projects the voxel at x, y, z to 2d image coordinates and add to lookup
                    x_img, y_img = project(np.array([x,y,z], dtype = "float64"), cam)
                    pixel = int(x_img), int(y_img)
                    voxel = (x,y,z)
                    self.add(pixel, voxel)
    
def project(voxel, cam: camera):
    """Projects a 3D voxel onto the 2D image of the specified camera"""
    [[imagepoints]], _ = cv.projectPoints(voxel, cam.rvec, cam.tvec, cam.matrix, cam.distcoeffs)
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
        voxels = voxelgrid(8, 8, 8)
        cameras.append(camera(camera_path, voxels))
    
    for cam in cameras:
        cam.initializeTable()
        subtracted_video = cam.path + "subtracted.avi"
        cap = cv.VideoCapture(subtracted_video)
        ret, image = cap.read()
        # cv.imshow('img',image)
        cv.waitKey()
        cap.release()
        cam.populateVoxelgrid(image)

