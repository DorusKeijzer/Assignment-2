import cv2 as cv 
import math
import numpy as np

def averagebackground(video, samplefrequency):
    cap = cv.VideoCapture
    framenumber = 0
    samples = []
    if True:
        if framenumber % samplefrequency == 0:
            samples.append(cap.read())
        framenumber +=1
    return np.mean(samples)


def euclideanDistance(tuple1, tuple2):
    """Difference is the root of the sum of the square of the differences"""
    result = 0
    for x,y in zip(tuple1, tuple2):
        result += abs(math.pow(x-y,2))
    return math.sqrt(result)

def subtractBackground(image, background, distanceFunction, threshold):
    """image and background are assumed to be the same size
    distanceFunction is assumed to be a function"""
    cv.imread(image)
    cv.imread(background)
    outputImage = np.zeroes((image.width, image.height))

    for x in image.width:
        for y in image.height:
            difference = distanceFunction(image[x,y], background[x,y])
            if difference > threshold:
                outputImage[x,y] = 1
    return outputImage

def erode(image):
    pass

def dilate(image):
    pass