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

    avg_gray = cv.GaussianBlur(avg_gray, (3, 3), 0)

    frame_width = int(cap.get(3)) 
    frame_height = int(cap.get(4)) 
    size = (frame_width, frame_height) 
    
    fourcc = cv.VideoWriter_fourcc('M','J','P','G')

    # writes to data/camX/subtracted.avi
    result = cv.VideoWriter(cam + 'subtracted.avi',  
                            fourcc, 
                            frame_rate, size) 

    while True:
        ret, frame = cap.read()
        if ret:
            gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            gray_frame = cv.GaussianBlur(gray_frame, (3, 3), 0)
            gray_frame_float = np.asfarray(gray_frame, dtype=float)
            difference = cv.absdiff(avg_gray, gray_frame_float)
            
            foreg = cv.absdiff(avg_gray, difference)
            
            difference = np.uint8(np.clip(difference, 0, 255))
            _, difference = cv.threshold(difference, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)


            # Apply erosion and dilation to the difference image
            kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))
            difference = cv.dilate(difference, kernel, iterations=1)
            difference = cv.erode(difference, kernel, iterations=1)

            contours, hierarchy = cv.findContours(difference, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)


            # Find the largest contour
            max_area = 0
            max_contour = None
            for cnt in contours:
                area = cv.contourArea(cnt)
                if area > max_area:
                    max_area = area
                    max_contour = cnt

            # Draw the largest contour on the original image
            if max_contour is not None:
                cv.drawContours(frame, [max_contour], -1, (0, 255, 0), 2)


            #cv.imshow("subtracted_frame", subtracted_frame)
            cv.imshow("difference", difference)
            # cv.imshow("frame", frame)
            # cv.imshow("foreground", foreg)
            # cv.imshow("grayframe", gray_frame)
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