import cv2
import os

def extractFrames(videoID,FPS):
	vidcap = cv2.VideoCapture(videoID)
	# -12 since assumes -trimmed.mp4
	# -4 if just .mp4
	videoID = videoID[:-12]
	success,image = vidcap.read()
	curr = 0
	fcount = 1
	#wait = 1.0/FPS
	#numFrames = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
	vidFPS = vidcap.get(cv2.CAP_PROP_FPS)
	#numSecs = int (numFrames/vidFPS)
	FPS = int ((vidFPS/FPS))
	while success:
		if curr == 0:
			os.mkdir(videoID)
		success,image = vidcap.read()
		if curr % FPS == 0:
			cv2.imwrite(videoID+'/'+videoID+'%03d.jpg' % fcount, image)
			fcount += 1
		curr += 1
	vidcap.release()

