import torch
import glob
import math
from PIL import Image
import numpy as np

#videoID - also the name of the folder with the frames
#frameStep - how frequently we check the frames (ex: if frameStep = 7,
#            we check every 7 frames and compare only those to count the
# 	         number of scene changes)
#totalNumSplits - number of splits made of each frame (how precise we want
#            to subtract each frame from each other)

def sceneChangeFilter(videoID,downloaded_path,frameStep,totalNumSplits):
	video_path = os.path.join(downloaded_path, videoID)
	frames_path = os.path.join(video_path, "Frames")
	filelist = glob.glob(os.path.join(frames_path,'*.jpg'))
	filelist.sort()

	frameNumbers = [i for i in range (len(filelist)) if i % frameStep == 0]
	frameArray = np.array([np.array(Image.open(filelist[fcount]),
		dtype=np.float64) for fcount in frameNumbers])

	# Makes exact copy of frameArray starting from index 1 (so one element smaller)
	frameArray2 = frameArray[1:]

	# Gets rid of last element in frameArray so frameArray and frameArray2 have equal size
	frameArray = frameArray[:-1]

	# Assumes the two frames are the same size
	numSplits = int (math.sqrt(totalNumSplits))
	splitDim1 = int (frameArray.shape[1]/numSplits)
	splitDim2 = int (frameArray.shape[2]/numSplits)

	frameTensors = torch.from_numpy(frameArray)
	frameTensors2 = torch.from_numpy(frameArray2)

	# If the image is 1280x720, its stored as 720x1280, this leaves it like 720x1280
	# frameTensors = frameTensors.view(-1,numSplits,numSplits,splitDim1,splitDim2,3)
	# frameTensors2 = frameTensors2.view(-1,numSplits,numSplits,splitDim1,splitDim2,3)

	# If the image is 1280x720, its stored as 720x1280, this flips it back to 1280x720
	frameTensors = frameTensors.view(-1,numSplits,numSplits,splitDim2,splitDim1,3)
	frameTensors2 = frameTensors2.view(-1,numSplits,numSplits,splitDim2,splitDim1,3)

	diff = frameTensors-frameTensors2

	result = torch.mul(diff,diff)
	result = result.view(-1,numSplits,numSplits,splitDim1*splitDim2*3)
	result = torch.sum(result,dim=3)

	cTemp = np.repeat(splitDim1*splitDim2*3*3025,result.shape[0]*result.shape[1]*result.shape[2])
	comparison = torch.from_numpy(cTemp).double().view(-1,numSplits,numSplits)

	sceneChange = result - comparison
	sceneChange[sceneChange<0] = 0

	numSC = [i for i in range (sceneChange.shape[0]) if torch.nonzero(sceneChange[i]).shape[0] > totalNumSplits/2]

	return (len(numSC) < 10)
