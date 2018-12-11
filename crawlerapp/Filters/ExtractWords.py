import os
from os import listdir
from os.path import isfile, join
import time
import numpy
import h5py

#SCRIPT TO CREATE PLAIN WORDS BASED ON THE GLOBAL TIMESTAMPS - words in each video and timestamps, only one segment that is the big video


#top='/media/backuphandle/MOSEI/MOSEI/MOSEI/Raw/Transcript/Segmented/Combined/'
#destination='/media/backuphandle/MOSEI/MOSEI/MOSEI/MMSDKCompatible/video_level/MOSEI_TimestampedWords.mtd'
#p2fadir='/media/backuphandle/MOSEI/MOSEI/MOSEI/Raw/Transcript/Full/Alignment/P2FA/Combined/'
#files = [f.split('.')[0] for f in listdir(top) if isfile(join(top, f))]

#data={}
#allwordsP2FA={}

def readP2FA(infile):
	allwordsP2FA = {}
	timestamps=[]
	with open(infile,'r') as fileptr:
		content=fileptr.read()
		wordcontent=content.split('"word"')[1].split('\n')
		if(wordcontent[0]==''):
			del wordcontent[0]
		if(wordcontent[-1]==''):
			wordcontent.pop()
		if((len(wordcontent)%3)!=0):
			print('Div not zero %s'%filename)
		totalwords=int(wordcontent[2])
		counter_words=0
		for i in range(3,len(wordcontent),3):
			counter_words+=1
			timestamp=[wordcontent[i+2][1:-1].lower(),float(wordcontent[i]),float(wordcontent[i+1])]
			allwordsP2FA[timestamp[0]]=None
			timestamps.append(timestamp)
		if(counter_words!=totalwords):
			print ("Wordcount inconsistency in %s"%file)
		s,e=float(content.split('\n')[3]),float(content.split('\n')[4])
	return timestamps,s,e





#for f in files:
#	data[f]={}
#		data[f]['0']['intervals']=numpy.zeros([1,2])
#		data[f]['0']['intervals'][0,0]=float(start)
#		data[f]['0']['intervals'][0,1]=float(end)
#		data[f]['0']['features']=numpy.array([features.split()],dtype=numpy.dtype('a64'))
#	print(count)
#	count+=1
#	timestamps=timestampss[f]
	#The entire segment length
#	s=ss[f]
#	e=es[f]
#	features=[[entry[0]]  for entry in timestamps]
#	featuresnp=numpy.array(features,dtype="a32")
#	print(featuresnp.shape,featuresnp[0,0])
#	intervals=numpy.array([[float(entry[1]),float(entry[2])] for entry in timestamps])

#	if(featuresnp.shape[0] != intervals.shape[0]):
#		print("Different size of intervals and featuers")
#		print(featuresnp.shape,intervals.shape)
#		time.sleep(1000)


#	data[f]={}
#	data[f]['intervals']=intervals
#	data[f]['features']=featuresnp

#words=mmdatasdk.computational_sequence("words")
#words.setData(data,'words')
#words.deploy(destination)

def extractWords(p2fa_file, destination, video_id):
	data = {}
	#The entire segment length
	timestamps,s,e=readP2FA(p2fa_file)
	features=[[entry[0]] for entry in timestamps]
	featuresnp=numpy.array(features,dtype="a32")
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
