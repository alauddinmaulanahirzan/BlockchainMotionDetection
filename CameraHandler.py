# import the opencv library
import cv2 # pip3 install opencv-python
import imutils
import numpy as np
import numpy

class CameraHandler:
    def initCamera():
        camera = cv2.VideoCapture(0)
        return camera

    def closeCamera(camera):
        camera.release()

    def getFrame(camera):
        ret, frame = camera.read()
        frame = imutils.resize(frame, height=720)
        frame = imutils.rotate(frame, 180)
        # cv2.imshow("frame",frame)
        # OpenCV Requirements
        if cv2.waitKey(1) & 0xFF == ord('q'):
            pass
        return frame

    def doCompare(frame1,frame2,motion):
        percentage = 0
        # Do Comparison
        height = frame2.shape[0]
        width = frame2.shape[1]
        res = np.zeros((height, width), dtype=np.uint8)
        # Convert to Grayscale
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        # Denoising
        gray1 = cv2.GaussianBlur(gray1, (25, 25), 0)
        gray2 = cv2.GaussianBlur(gray2, (25, 25), 0)
        # Find Delta
        deltaframe = cv2.absdiff(gray1,gray2)
        threshold = cv2.threshold(deltaframe, 25, 255, cv2.THRESH_BINARY)[1]
        threshold = cv2.dilate(threshold,None)
        countour = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Find Difference Percentage
        if(countour[1] is not None):
            percentage = (countour[0][0].size/len(res))*100
        else:
            percentage = (len(data[0])/len(res))*100
        if(countour[1] is None):
            motion = False
        else:
            motion = True
        return motion,percentage

def main():
    # Parameters
    camera = None
    frame1 = None
    frame2 = None
    motion = None
    percentage = None
    # Camera Start
    camera = CameraHandler.initCamera()
    while(True):
        frame = CameraHandler.getFrame(camera)
        if(frame1 is None):
            frame1 = frame
        else:
            frame2 = frame
            motion,percentage = CameraHandler.doCompare(frame1,frame2,motion,percentage)
            frame1 = frame2
            print(motion,percentage)
    CameraHandler.closeCamera(camera)

if __name__ == '__main__':
    main()
