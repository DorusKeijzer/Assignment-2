import cv2 as cv
from constants import *
import glob
import numpy as np
import assignment

# allows us to iterate over the camera folders
cams = glob.glob("../data/*/")

class lookuptableData:
    def __init__(self, cam, voxel_coords, image_coords):
        self.cam = cam
        self.voxel_coords = voxel_coords
        self.image_coords = image_coords

class table:
    def __init__(self):
        self.table = []

    def addPixel(self, item):
        self.table.append(item)

    def createTable(self, voxels):
        for voxel in voxels:
            for i, cam in enumerate(cams): 
                x_img, y_img = project(voxel, cam)
                self.addPixel(lookuptableData(i, voxel, (x_img, y_img)))

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

def project():
    raise NotImplementedError

def isForeGround(pixel):
    raise NotImplementedError

if __name__ == "__main__":
    
    image = np.zeros((256,256))
    cv.circle(image, (128, 128), 64, 200, 1)

    for x in image:
        if np.any(x):
            x = False
        else:
            x = True

    print(image)



    LookupTable = table()
    LookupTable.createTable(voxels)
