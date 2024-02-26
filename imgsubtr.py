import cv2 as cv
import numpy as np
import glob 

cams = glob.glob("data/*/")

if __name__ == "__main__":
    for cam in cams:
        print(f"reading {cam}")
        backg = cv.VideoCapture(cam + "background.avi")
        cap = cv.VideoCapture(cam + "video.avi")
        frame_rate = cap.get(cv.CAP_PROP_FPS)

        # TODO hier nog de averaging van de frames aan toevoegen
        _, first_frame = backg.read()
        first_gray = cv.cvtColor(first_frame, cv.COLOR_BGR2GRAY)
        first_gray = cv.GaussianBlur(first_gray, (5, 5), 0)
    
        frame_width = int(cap.get(3)) 
        frame_height = int(cap.get(4)) 
        size = (frame_width, frame_height) 
        # TODO voorbereiden bestand
        
        fourcc = cv.VideoWriter_fourcc('M','J','P','G')

        # writes to data/camX/subtracted.avi
        result = cv.VideoWriter(cam + 'subtracted.avi',  
                                fourcc, 
                                frame_rate, size) 

        while True:
            ret, frame = cap.read()
            if ret:
                gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                gray_frame = cv.GaussianBlur(gray_frame, (5, 5), 0)
                difference = cv.absdiff(first_gray, gray_frame)
                _, difference = cv.threshold(difference, 25, 255, cv.THRESH_BINARY)
                # cv.imshow("First frame", first_frame)
                # cv.imshow("Frame", frame)
                if len(difference.shape) == 2:
                    difference = cv.cvtColor(difference, cv.COLOR_GRAY2BGR)

                cv.imshow("difference", difference)
                result.write(difference)
            else:
                break
            key = cv.waitKey(20)
            if key == 27:
                break

        cap.release()
        result.release()
        print(f"Wrote to {cam}subtracted.avi")

        cv.destroyAllWindows()
            