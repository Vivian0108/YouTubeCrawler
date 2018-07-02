import cv2
import glob
import torch
import math
from PIL import Image
import numpy as np
import os

count = 1

def faceDetect(videoID, downloaded_path):
    video_path = os.path.join(downloaded_path, videoID)
    frames_path = os.path.join(video_path, "Frames")
    fcascade = cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_alt.xml")
    scascade = cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_profileface.xml")
    filelist = glob.glob(os.path.join(frames_path,'*.jpg'))
    print(filelist)
    filelist.sort()

    frameArray = np.array([np.array(detect(fname,fcascade,scascade,videoID), dtype=np.float64) for fname in filelist])
    frameTensor = torch.from_numpy(frameArray)

    size = frameTensor.shape[0]
    oneFace = torch.nonzero(frameTensor)
    frameTensor[frameTensor<=1] = 0
    moreFaces = torch.nonzero(frameTensor)

    global count
    count = 1
    #print (oneFace.shape[0])
    #print (moreFaces.shape[0])
    #Choose the percentage (0.75) of the total frames that must contain faces
    return [oneFace.shape[0] >= int (0.75 * size),moreFaces.shape[0] >= int (0.75 * size)]


def detect(path,front_cascade,side_cascade,videoID):
    img = cv2.imread(path)
    #flipped_img = cv2.flip(img, 1)
    # img = cv2.resize(img,(int(img.shape[1]*1000/img.shape[0]),1000))
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #gray_flip = cv2.cvtColor(flipped_img, cv2.COLOR_BGR2GRAY)
    #rects = cascade.detectMultiScale(gray_img, 1.05, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (10,10))
    #frontal faces
    frects = front_cascade.detectMultiScale(gray_img, 1.2, 4, cv2.CASCADE_SCALE_IMAGE, (30,30))
    #right side faces
    # s1rects = side_cascade.detectMultiScale(gray_img, 1.2, 4, cv2.CASCADE_SCALE_IMAGE, (30,30))
    # #left faces
    # s2rects = side_cascade.detectMultiScale(gray_flip, 1.2, 4, cv2.CASCADE_SCALE_IMAGE, (30,30))
    # box(frects, s1rects, s2rects, img, videoID)
    #box(frects, img, videoID)

    return len(frects) #+ len(s1rects) + len(s2rects)
    #len(rects) represents the number of faces
    # if len(rects) == 0:
    #     return [], img
    # rects[:, 2:] += rects[:, :2]
    # return rects, img

# for testing purposes to see what the detect faces are, when actually running comment out the box line
# def box(frects, s1rects, s2rects, img, videoID):
def box(frects, img, videoID):
    width = img.shape[1]
    for x1, y1, x2, y2 in frects:
        #cv2.rectangle(img, (x1, y1), (x2, y2), (127, 255, 0), 2)
        cv2.rectangle(img, (x1, y1), (x1+x2, y1+y2), (0, 255, 0), 2)
    # for x1, y1, x2, y2 in s1rects:
    #     #cv2.rectangle(img, (x1, y1), (x2, y2), (127, 255, 0), 2)
    #     cv2.rectangle(img, (x1, y1), (x1+x2, y1+y2), (0, 255, 0), 2)
    # for x1, y1, x2, y2 in s2rects:
    #     #cv2.rectangle(img, (x1, y1), (x2, y2), (127, 255, 0), 2)
    #     cv2.rectangle(img, (width-x1, y1), (width-x1-x2, y1-y2), (0, 255, 0), 2)
    global count
    cv2.imwrite(videoID + '/' + 'detected'+'%03d.jpg' % count, img)
    count += 1
