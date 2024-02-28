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


# def get_cam_rotation_matrices():
#     # Generates dummy camera rotation matrices, looking down 45 degrees towards the center of the room
#     # TODO: You need to input the estimated camera rotation matrices (4x4) of the 4 cameras in the world coordinates.
    
#     cam_angles = []
#     for camera_path in camera_paths:
#         [rvec] = readXML(camera_path + "configs.xml", "Rvec")
#         # R, _ = cv.Rodrigues(rvec) # turns rvec into rotation matrix
#         # print(R)
#         # rotation_matrix = glm.mat4(
#         #     R[0][0], R[1][0], R[2][0], 0,
#         #     R[0][1], R[1][1], R[2][1], 0,
#         #     R[0][2], R[1][2], R[2][2], 0,
#         #     0, 0, 0, 1
#         # )
#         cam_angles.append([rvec])
        
#         #cam_angles = [[0, 45, -45], [0, 135, -45], [0, 225, -45], [0, 315, -45]]
#         cam_rotations = [glm.mat4(1), glm.mat4(1), glm.mat4(1), glm.mat4(1)]
#         for c in range(len(cam_rotations)):
#             cam_rotations[c] = glm.rotate(cam_rotations[c], cam_angles[c][0] * np.pi / 180, [1, 0, 0])
#             cam_rotations[c] = glm.rotate(cam_rotations[c], cam_angles[c][1] * np.pi / 180, [0, 1, 0])
#             cam_rotations[c] = glm.rotate(cam_rotations[c], cam_angles[c][2] * np.pi / 180, [0, 0, 1])
        
#     return cam_rotations



def get_cam_rotation_matrices():
    # Generates dummy camera rotation matrices, looking down 45 degrees towards the center of the room
    # TODO: You need to input the estimated camera rotation matrices (4x4) of the 4 cameras in the world coordinates.
    cam_angles = np.degrees([[-0.06445+1.57, -0.16194+1.57, -0.19139+1.57], [-0.003235+1.57, -0.22278+1.57, -0.21884+1.57], [-0.12429, 0.101235, (0.10331 + np.pi)], [-0.072086+1.57, 0.15965+1.57, 0.17770+1.57]])
    #cam_angles = [[90,90,90],[-90,-90,-90],[5,5,5], [1,2,3]]
    cam_rotations = [glm.mat4(1), glm.mat4(1), glm.mat4(1), glm.mat4(1)]
    for c in range(len(cam_rotations)):
         cam_rotations[c] = glm.rotate(cam_rotations[c], cam_angles[c][0] * np.pi / 180, [1, 0, 0])
         cam_rotations[c] = glm.rotate(cam_rotations[c], cam_angles[c][1] * np.pi / 180, [0, 1, 0])
         cam_rotations[c] = glm.rotate(cam_rotations[c], cam_angles[c][2] * np.pi / 180, [0, 0, 1])
    return cam_rotations


# def get_cam_rotation_matrices():
#     # Generates dummy camera rotation matrices, looking down 45 degrees towards the center of the room
#     # TODO: You need to input the estimated camera rotation matrices (4x4) of the 4 cameras in the world coordinates.
#     cam_angles = [[0, 0, 0], [0, 0, 0], [0, 0, 0],[0, 0, 0]]
#     cam_rotations = [glm.mat4(1), glm.mat4(1), glm.mat4(1), glm.mat4(1)]
#     for c in range(len(cam_rotations)):
#         cam_rotations[c] = glm.rotate(cam_rotations[c], cam_angles[c][0] * np.pi / 180, [1, 0, 0])
#         cam_rotations[c] = glm.rotate(cam_rotations[c], cam_angles[c][1] * np.pi / 180, [0, 1, 0])
#         cam_rotations[c] = glm.rotate(cam_rotations[c], cam_angles[c][2] * np.pi / 180, [0, 0, 1])
#     return cam_rotations