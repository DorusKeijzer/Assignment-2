import cv2 as cv
from constants import *
import glob
import numpy as np
import assignment
from utils import readXML, debugMatrices
from collections import defaultdict

class camera:
    """Stores the properties of a camera
        path: path to the camera folder
        matrix: camera matrix
        distcoeffs: distortion coefficients
        rvec: rotation vector
        tvec: translation vector
        table: lookup table between image points and voxels
        voxelgrid: the voxels that are on or off from this cameras perspective
        shape"""
    matrix, distcoeffs, rvec, tvec, table, voxels = ..., ..., ... , ..., ..., ...
    
    def __init__(self, path, voxelgrid, scale):
        self.path = path
        self.matrix, self.distcoeffs, self.rvec, self.tvec = readXML(path+"configs.xml", "CameraMatrix", "DistortionCoeffs", "Rvec", "Tvec")
        self.voxels = voxelgrid
        self.table = table()
        self.table.populateTable(self.voxels.coordinates, self, scale)

        


    def __str__(self):
        return f"{self.path}\n\n{self.matrix}\n{self.distcoeffs}\n{self.rvec}\n{self.tvec}"



    def populateVoxelgrid(self, image):
        image = image[:,:,0]  # only takes one channel of the image
        for (x,y) in self.table.table.keys():
            pixel = image[x,y]
            if pixel > 25:
                image[x,y] = 125
            # if the pixel in the imge is on and inside the bounds of the image
            if pixel > 25 and self.table.inBounds((x,y)): 
                # look up the voxels corresponding to this pixel and set these voxels to True
                voxel_ray = self.table.lookup((x,y))
                if voxel_ray:
                    for index in voxel_ray:
                        self.voxels.state[index] = 1
        for x,y in self.table.table.keys():
            try:
                if len(self.table.lookup((x,y)))>0: 
                    image[x,y]+= 50
            except:
                pass


class voxelgrid:
    '''Array of voxel coordinates. The order is shared between all instances of camera'''
    coordinate, state, shape = ..., ..., ...

    def __init__(self, x_bound, y_bound, z_bound, scale, translation):
        """coordinates: stores 3D coordinates of a voxel
        state: whether this point is on or off for a given view
        shape: the size of the voxel array"""
        self.coordinates = np.mgrid[-x_bound/2:x_bound/2,-y_bound/2:y_bound/2,-z_bound/2:z_bound].T.reshape(-1, 3)
        self.coordinates = self.coordinates.astype("float64") + translation
        self.state = np.zeros(self.coordinates.shape[0], dtype = bool)
        self.shape = (x_bound, y_bound, z_bound)

    
class table:
    """A lookup table mapping voxels to image pixels for a given camera
    table: a dictionary of lists
    
    bounds give the highest and lowest image coordinte in each direction"""
    table = ...
    # gives the maximum and minimum values 
    x_lowbound, x_highbound, y_lowbound, y_highbound = ..., ...,  ..., ... 
    
    def __init__(self):
        self.table = defaultdict()
        self.x_lowbound, self.x_highbound, self.y_lowbound, self.y_highbound = None, None, None, None

    def __str__(self):
        res = ""
        for key, value in self.table.items():
            res += (f"{key}, {value}\n")
        res += self.bounds()
        return res
    
    def bounds(self):
        """String giving the bounds"""
        return f"x-bounds: {self.x_lowbound}, {self.x_highbound}\ny-bounds: {self.y_lowbound}, {self.y_highbound}"

    def add(self, pixel: tuple[int,int], voxel: tuple[int,int,int]):
        """"Adds the pixel to the lookup table and adjusts the bounds accordingly"""
        try:
            self.table[pixel].append(voxel)
        except:
            self.table[pixel] = [voxel]
        self.adjustbounds(pixel)

    def adjustbounds(self,pixel: tuple[int,int]):
        """Sets or increases/decreases the bounds via the given pixel """
        x,y = pixel
        # assumes either all bounds are set or none are
        if not (self.x_lowbound or self.x_highbound or self.y_lowbound or self.y_highbound):
            self.x_lowbound, self.x_highbound, self.y_lowbound, self.y_highbound = x, x, y, y
        # if the pixel is outside of bounds, adjust the bounds
        if x < self.x_lowbound:
            self.x_lowbound = x
        elif x > self.x_highbound:
            self.x_highbound = x
        if y < self.y_lowbound:
            self.y_lowbound = y
        elif y > self.y_highbound:
            self.y_highbound = y

    def inBounds(self, coordinate: tuple[int,int]) -> bool:
        """True if the coordinate is inbetween the bounds, otherwise false"""
        x, y = coordinate
        return self.x_lowbound < x < self.x_highbound and self.y_lowbound < y < self.y_highbound

    def lookup(self, pixel: tuple[int, int]):
        """Returns a list of voxels given a pixel"""
        try: 
            voxel = self.table[pixel] 
        except Exception as e:
            print(self.bounds())
            raise e
        return voxel

    def populateTable(self, voxels, cam: camera, scale):

        """Projects every voxel onto image pixels"""
        imagepoints, _ = cv.projectPoints((voxels * scale).astype("float32"), cam.rvec, cam.tvec, cam.matrix, cam.distcoeffs)
        for index, [[x,y]] in enumerate(imagepoints):
             if x< 486 and y < 644:
                pixelcoords = (int(x), int(y))
                self.add(pixelcoords, index)
    
def setVoxels(cameras: list[camera], scale, translation)-> voxelgrid:
    """Returns a voxelgrid that contains the intersections of all views (cameras)"""
    # creates a new voxelgrid of the same size (assuming all voxelgrids are of the same size (cause they should be))
    xsize, ysize, zsize = cameras[0].voxels.shape
    result = voxelgrid(xsize, ysize, zsize, scale, translation)

    # for all pixels: if pixel is on in all views, set pixel to 1, otherwise 0
    for index in range(len(cameras[0].voxels.state)):
        combineCameras(cameras, index)
    return result

def combineCameras(cameras: list[camera], index)->bool:
    """Takes the intersection of all cameras"""
    for camera in cameras:
        if camera.voxels.state[index] == False:
            return False
    return True

camera_paths = glob.glob("data/*/")
cameras = []

SCALE = 25
TRANSLATION = np.array([0,40,0])
print("Initializing Lookup tables...")
for i, camera_path in enumerate(camera_paths,1):
    print(f"Initializing lookup table {i}", end="\r")
    voxels = voxelgrid(64, 64,64, SCALE, TRANSLATION)
    cameras.append(camera(camera_path, voxels, SCALE))
    print(f"Initialized lookup table {i} ")
print("Lookup tables initialized.\n\nInitializing voxel grids...")

caps = []
for cam in cameras:
    subtracted_video = cam.path + "subtracted.avi"
    cap = cv.VideoCapture(subtracted_video)
    caps.append(cap)

camsNcaps = zip(cameras, caps)
for cam, cap in camsNcaps:
    ret, image = cap.read()
    cap.release()
    cam.populateVoxelgrid(image)
    cv.rectangle(image, 
                 (cam.table.y_lowbound, cam.table.x_lowbound), 
                 (cam.table.y_highbound, cam.table.x_highbound), 
                 (0,0,255),
                 2,
                 2,)
    cv.imshow(cam.path,image)
    print(cam.voxels.state.any())
cv.waitKey()
FinalGrid = setVoxels(cameras, SCALE, TRANSLATION)
print(FinalGrid.state.any())

