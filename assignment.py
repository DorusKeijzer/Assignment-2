import glm
import random
import numpy as np
from utils import readXML
import glob
import cv2 as cv

block_size = 1.0

camera_paths = glob.glob("data/*/")

def generate_grid(width, depth):
    # Generates the floor grid locations
    # You don't need to edit this function
    data, colors = [], []
    for x in range(width):
        for z in range(depth):
            data.append([x*block_size - width/2, -block_size, z*block_size - depth/2])
            colors.append([1.0, 1.0, 1.0] if (x+z) % 2 == 0 else [0, 0, 0])
    return data, colors


def set_voxel_positions(width, height, depth):
    # Generates random voxel locations
    # TODO: You need to calculate proper voxel arrays instead of random ones.
    data, colors = [], []
    for x in range(width):
        for y in range(height):
            for z in range(depth):
                if random.randint(0, 1000) < 5:
                    data.append([x*block_size - width/2, y*block_size, z*block_size - depth/2])
                    colors.append([x / width, z / depth, y / height])
    return data, colors


def get_cam_positions():
    # Generates dummy camera locations at the 4 corners of the room
    # TODO: You need to input the estimated locations of the 4 cameras in the world coordinates.
    translations = []

    for camera_path in camera_paths:
        tvec, rvec   = readXML(camera_path + "configs.xml", "Tvec", "Rvec")
        R, _ = cv.Rodrigues(rvec)
        translations.append(-np.dot(R.T, tvec).flatten())
    translations = np.array([[x,-z,y] for x,y,z in translations]) # TODO not sure why -z instead of z
    translations = translations / 100 # converts mm to m, to make it fit on the scene
    
    return translations, [[1.0, 0, 0], [0, 1.0, 0], [0, 0, 1.0], [1.0, 1.0, 0]]


def get_cam_rotation_matrices():
    # Generates dummy camera rotation matrices, looking down 45 degrees towards the center of the room
    # TODO: You need to input the estimated camera rotation matrices (4x4) of the 4 cameras in the world coordinates.
    # cam_angles =[]
    cam_rotations = []
    for camera_path in camera_paths:
        [rvec] = readXML(camera_path + "configs.xml", "Rvec")
        R, _ = cv.Rodrigues(rvec) # turns rvec into rotation matrix
        print(R)
        rotation_matrix = glm.mat4(
            R[0][0], R[1][0], R[2][0], 0,
            R[0][1], R[1][1], R[2][1], 0,
            R[0][2], R[1][2], R[2][2], 0,
            0, 0, 0, 1
        )
        cam_rotations.append(rotation_matrix)
        
    return cam_rotations
