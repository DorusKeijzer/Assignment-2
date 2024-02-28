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
    matrix, distcoeffs, rvec, tvec, table, voxels = ..., ..., ... , ..., ..., ...
    
    def __init__(self, path, voxelgrid):
        self.path = path
        self.matrix, self.distcoeffs, self.rvec, self.tvec = readXML(path+"configs.xml", "CameraMatrix", "DistortionCoeffs", "Rvec", "Tvec")
        self.voxels = voxelgrid
        self.table = table()
        self.table.populateTable(self.voxels, self)



    def populateVoxelgrid(self, image):
        image = image[:,:,0]  # only takes one channel of the image
        for x in range(image.shape[0]):
            for y in range(image.shape[1]):
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
# class voxelgrid:
#     """Grid: 3D np array that contains whether a voxel is on
#     Size: a three-tuple of the size in each direction"""
#     def __init__(self,x,y,z):
#         self.grid = np.zeros((x,y,z), dtype=bool)
#         self.shape = self.grid.shape
    
#     def __str__(self):
#         return str(self.grid)
    

class voxelgrid:
    '''Array of voxel coordinates. The order is shared between all instances of camera'''
    coordinate, state, shape = ..., ..., ...

    def __init__(self, x_bound, y_bound, z_bound, scale, translation):
        """coordinates: stores 3D coordinates of a voxel
        state: whether this point is on or off for a given view
        shape: the size of the voxel array"""
        x_values = np.arange(x_bound)
        y_values = np.arange(y_bound)
        z_values = np.arange(z_bound)
        
        xx, yy, zz = np.meshgrid(x_values, y_values, z_values, indexing='ij')
        self.coordinates = np.column_stack((xx.ravel(), yy.ravel(), zz.ravel())) * scale
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
        self.table = {}
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
            # print(self.bounds())
            raise e
        return voxel

    def populateTable(self, voxels, cam: camera):
        """Projects every voxel onto image pixels"""
        for index, voxel in enumerate(cam.voxels.coordinates):

            # projects the voxel at x, y, z to 2d image coordinates, 
            # and adds the pixel and the voxel index to the lookup table
            x_img, y_img = project(voxel, cam)
            pixel = tuple(np.round((x_img, y_img)).astype(int))
            self.add(pixel, index)

        # adds an empty list to each pixel that is in bounds but does not correspond with a voxel
        for x in range(self.x_lowbound, self.x_highbound+1):
            for y in range(self.y_lowbound, self.y_highbound+1):
                if (x,y) not in self.table.keys():
                    self.table[(x,y)] = None
    
def project(voxel: np.array, cam: camera):
    """Projects a 3D voxel onto the 2D image of the specified camera"""
    [[imagepoints]], _ = cv.projectPoints(voxel, cam.rvec, cam.tvec, cam.matrix, cam.distcoeffs)
    return imagepoints

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
SCALE = 20
TRANSLATION = np.array([0,0,0])
print("Initializing Lookup tables...")
for i, camera_path in enumerate(camera_paths,1):
    print(f"Initializing lookup table {i}", end="\r")
    voxels = voxelgrid(64, 64,64, SCALE, TRANSLATION)
    cameras.append(camera(camera_path, voxels))
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
    x,y = project(np.array([0,0,0], dtype="float64"), cam)
    x,y = int(x), int(y)
    cv.circle(image, (x,y), 3, (0,0,200), 3)
    cv.imshow(cam.path,image)
    print(cam.voxels.state.any())
cv.waitKey()
FinalGrid = setVoxels(cameras, SCALE, TRANSLATION)
print(FinalGrid.state.any())
