import os
from os import listdir
from os.path import isfile, join
import time
import numpy
import h5py

#SCRIPT TO CREATE PLAIN WORDS BASED ON THE GLOBAL TIMESTAMPS - words in each video and timestamps, only one segment that is the big video


#top='/media/backuphandle/MOSEI/MOSEI/MOSEI/Raw/Transcript/Segmented/Combined/'
#destination='/media/backuphandle/MOSEI/MOSEI/MOSEI/MMSDKCompatible/video_level/MOSEI_TimestampedPhones.csd'
#p2fadir='/media/backuphandle/MOSEI/MOSEI/MOSEI/Raw/Transcript/Full/Alignment/P2FA/Combined/'
#files = [f.split('.')[0] for f in listdir(top) if isfile(join(top, f))]

#data={}

def readP2FAPhones(infile):
	timestamps=[]
	ss={}
	es={}
	with open(infile,'r') as fileptr:
		timestamp=[]
		content=fileptr.read().split('\n')
		phonecontent=content[content.index("\"phone\"")+4:content.index("\"word\"")-1]
		if((len(phonecontent)%3)!=0):
			print('Div not zero %s'%filename)
			time.sleep(100)
		totalphones=int(content[content.index("\"phone\"")+3])
		if totalphones != (len(phonecontent)/3):
			print("Length is not accurate")
			time.sleep(100)
		counter_phones=0
		for i in range(0,len(phonecontent),3):
			counter_phones+=1
			timestamp=[phonecontent[i+2][1:-1].lower(),float(phonecontent[i]),float(phonecontent[i+1])]
			timestamps.append(timestamp)
		if(counter_phones!=totalphones):
			print ("Phonecount inconsistency in %s"%file)
			time.sleep(100)
	return timestamps


#count=0
#timestampss=readP2FAPhones(files)
#print ("P2FA Phones DID")

#for f in files:
#	print(count)
#	count+=1
#	timestamps=timestampss[f]
#	#The entire segment length
#	features=[[entry[0]]  for entry in timestamps]
#	featuresnp=numpy.array(features,dtype="a8")
#	print(featuresnp.shape,featuresnp[0,0])
#	intervals=numpy.array([[float(entry[1]),float(entry[2])] for entry in timestamps])

#	if(featuresnp.shape[0] != intervals.shape[0]):
#		print("Different size of intervals and featuers")
#		print(featuresnp.shape,intervals.shape)
#		time.sleep(1000)


#	data[f]={}
#	data[f]['intervals']=intervals
#	data[f]['features']=featuresnp


def extractPhones(p2fa_file, destination, video_id):
	data = {}
	timestamps = readP2FAPhones(p2fa_file)
	#The entire segment length
	features=[[entry[0]]  for entry in timestamps]
	featuresnp=numpy.array(features,dtype="a8")
	print(featuresnp.shape,featuresnp[0,0])
	intervals=numpy.array([[float(entry[1]),float(entry[2])] for entry in timestamps])

	if(featuresnp.shape[0] != intervals.shape[0]):
		print("Different size of intervals and featuers")
		print(featuresnp.shape,intervals.shape)
		time.sleep(1000)


	data[video_id]={}
	data[video_id]['intervals']=intervals
	data[video_id]['features']=featuresnp

	write5Handle=h5py.File(destination,'w')

	vidHandle=write5Handle.create_group(video_id)
	vidHandle.create_dataset("features",data=data[video_id]["features"])
	vidHandle.create_dataset("intervals",data=data[video_id]["intervals"])
	write5Handle.close()
