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
        for x in range(image.shape[0]):
            for y in range(image.shape[0]):
                pixel = image[x,y]
                # if the pixel in the imge is on and inside the bounds of the image
                if pixel != 0 and self.table.inBounds((x,y)): 
                    # look up the voxels corresponding to this pixel  
                    voxel_ray = self.table.lookup((x,y))
                    for voxel in voxel_ray:
                        # set this voxel to one for this camera
                        self.voxelgrid[voxel] = 1

class voxelgrid:
    """Grid: 3D np array that contains whether a voxel is on
    Size: a three-tuple of the size in each direction"""
    def __init__(self,x,y,z):
        self.grid = np.zeros((x,y,z))
        self.shape = self.grid.shape
    
    def __str__(self):
        return str(self.grid)
    
    
class table:
    """A lookup table mapping voxels to image pixels for a given camera
    table: a dictionary of lists
    
    bounds give the highest and lowest image coordinte in each direction"""
    table = ...
    # gives the maximum and minimum values 
    x_lowbound, x_highbound, y_lowbound, y_highbound = ..., ...,  ..., ... 
    
    def __init__(self):
        self.table = {}
        self.x_lowbound, self.x_highbound, self.y_lowbound, self.y_highbound = None, None, None, None

    def __str__(self):
        res = ""
        for key, value in self.table.items():
            res += (f"{key}, {value}\n")
        res += self.bounds()
        return res
    
    def bounds(self):
        """Prints the bounds """
        return f"x-bounds: {self.x_lowbound}, {self.x_highbound}\ny-bounds: {self.y_lowbound}, {self.y_highbound}"

    def add(self, key, value):
        """"Adds the key to the lookup table and adjusts the bounds accordingly"""
        try:
            self.table[key].append(value)
        except:
            self.table[key] = [value]
        self.adjustbounds(key)

    def adjustbounds(self,key):
        """Sets or increases/decreases the bounds via the given key """
        x,y = key
        # assumes either all bounds are set or none are
        if not self.x_lowbound or self.x_highbound or self.y_lowbound or self.y_highbound:
            self.x_lowbound, self.x_highbound, self.y_lowbound, self.y_highbound = x, x, y, y
        # if the key is outside of bounds, adjust the bounds
        if x < self.x_lowbound:
            self.x_lowbound = x
        if x > self.x_highbound:
            self.x_highbound = x
        if y < self.y_lowbound:
            self.y_lowbound = y
        if y > self.y_highbound:
            self.y_highbound = y

    def inBounds(self, coordinate) -> bool:
        """True if the coordinate is inbetween the bounds, otherwise false"""
        x, y = coordinate
        return self.x_lowbound < x < self.x_highbound and self.y_lowbound < y < self.y_highbound

    def lookup(self, key):
        try: 
            res = self.table[key] 
        except Exception as e:
            print(self)
            print(key)

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

def setVoxels(cameras: list[camera])-> voxelgrid:
    """Returns a voxelgrid that contains the intersections of all views (cameras)"""
    # creates a new voxelgrid of the same size (assuming all voxelgrids are of the same size (cause they should be))
    xsize, ysize, zsize = cameras[0].voxelgrid.size
    result = voxelgrid(xsize, ysize, zsize)

    # for all pixels: if pixel is on in all views, set pixel to 1, otherwise 0
    for x in range(voxels.shape[0]):
        for y in range(voxels.shape[1]):
            for z in range(voxels.shape[2]):
                result.grid[x,y,z] = int(combineCameras(cameras, x,y,z))


def combineCameras(cameras: list[camera], x, y, z):
    """Given a list of views and x,y,z coordinates, return if the voxel at x,y,z is on in all views"""
    for camera in cameras:
        if camera.voxelgrid[x,y,z] == 0:
            return False
    return True
                    



if __name__ == "__main__":
    camera_paths = glob.glob("data/*/")
    cameras = []
    for camera_path in camera_paths:
        voxels = voxelgrid(16, 16, 16)
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
        print(cam.table.bounds())
