import cv2 as cv
import numpy as np
import glob 

cams = glob.glob("data/*/")
num_frames = 1

if __name__ == "__main__":
    for cam in cams:
        print(f"reading {cam}")
        backg = cv.VideoCapture(cam + "background.avi")
        cap = cv.VideoCapture(cam + "video.avi")
        frame_rate = cap.get(cv.CAP_PROP_FPS)
        total_gray = None

        for _ in range(num_frames):
            _, frame = backg.read()
            if frame is not None:
                gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                if total_gray is None:
                    total_gray = gray_frame.copy()
                else:
                    total_gray += gray_frame
            else:
                print("Error: Unable to read the frame from the video.")
                break
    
        if total_gray is not None:
            avg_gray = total_gray / num_frames
    
        else:
            print("Error: Unable to process the first frames.")
    else:
        print("Error: Unable to open the video file or stream.")


        # # TODO hier nog de averaging van de frames aan toevoegen
        # _, first_frame = backg.read()
        # avg_gray = cv.cvtColor(first_frame, cv.COLOR_BGR2GRAY)
        
        
        avg_gray = cv.GaussianBlur(avg_gray, (5, 5), 0)
    
        frame_width = int(cap.get(3)) 
        frame_height = int(cap.get(4)) 
        size = (frame_width, frame_height) 
        
        # TODO voorbereiden bestand
        fourcc = cv.VideoWriter_fourcc('M','J','P','G')

        # writes to data/camX/subtracted.avi
        result = cv.VideoWriter(cam + 'subtracted.mov',  
                                fourcc, 
                                frame_rate, size) 

        while True:
            ret, frame = cap.read()
            if ret:
                gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                gray_frame = cv.GaussianBlur(gray_frame, (5, 5), 0)
                gray_frame_float = np.asfarray(gray_frame,dtype = float)
                difference = cv.absdiff(avg_gray, gray_frame_float)
                _, difference = cv.threshold(difference, 25, 255, cv.THRESH_BINARY)
                # cv.imshow("First frame", first_frame)
                # cv.imshow("Frame", frame)
                
                
                # if len(difference.shape) == 2:
                #     difference = cv.cvtColor(difference, cv.COLOR_GRAY2BGR)


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
            