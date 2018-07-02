import cv2
import os
from crawlerapp.definitions import CONFIG_PATH

def extractFrames(videoID, FPS, video_path):
	frames_path = os.path.join(video_path, "Frames")
	vidcap = cv2.VideoCapture(video_path + ".mp4")
	success, image = vidcap.read()
	curr = 0
    fcount = 1
    # wait = 1.0/FPS
    # numFrames = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
    vidFPS = vidcap.get(cv2.CAP_PROP_FPS)
    # numSecs = int (numFrames/vidFPS)
    FPS = int((vidFPS / FPS))
    while success:
        if curr == 0:
            os.mkdir(frames_path)
        success, image = vidcap.read()
        if curr % FPS == 0:
			write_path = os.path.join(frames_path,videoID)
            cv2.imwrite(write_path + '%03d.jpg' % fcount, image)
        	fcount += 1
    	curr += 1
	vidcap.release()
