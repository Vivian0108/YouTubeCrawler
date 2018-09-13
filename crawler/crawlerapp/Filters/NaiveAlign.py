import numpy as np
import h5py
import os

def align_phones(file):
    raw_transcript = open(file,"r")
    sections = raw_transcript.read().split("\n\n")
    line_count = 0
    #times are on even lines on even segments and odd lines on odd segments
    segment = 0

    intervals = []
    features = []

    for section_num, section in enumerate(sections):
        if section_num > 0:
            try:
                times = section.split("\n")[0]
                words = section.split("\n")[1]
            except IndexError:
                #Empty line
                continue

            line_time = 0
            #At time stamp

            start_time = times[:12].replace(":","")
            end_time = times[17:].replace(":","")

            start_hours = start_time[0:2]
            start_minutes = start_time[2:4]
            start_seconds = start_time[4:10]
            start_total = float(start_hours)*3600+float(start_minutes)*60+float(start_seconds)

            end_hours = end_time[0:2]
            end_minutes = end_time[2:4]
            end_seconds = end_time[4:10]
            end_total = float(end_hours)*3600+float(end_minutes)*60+float(end_seconds)

            line_time = end_total - start_total

            letters = words.replace(" ", "")
            if len(letters) == 0:
                continue
            increment = line_time/len(letters)

            start = start_total
            end = start_total + increment
            for index,letter in enumerate(letters):
                interval = [start,end]
                intervals.append(interval)
                features.append(letter.encode("utf8"))
                start = end
                end = end+increment

    return intervals,features

def align_words(file):
    raw_transcript = open(file,"r")
    sections = raw_transcript.read().split("\n\n")
    line_count = 0
    #times are on even lines on even segments and odd lines on odd segments
    segment = 0

    intervals = []
    features = []

    for section_num, section in enumerate(sections):
        if section_num > 0:
            try:
                times = section.split("\n")[0]
                words = section.split("\n")[1].split(" ")
            except IndexError:
                #Empty line
                continue

            line_time = 0
            #At time stamp

            start_time = times[:12].replace(":","")
            end_time = times[17:].replace(":","")

            start_hours = start_time[0:2]
            start_minutes = start_time[2:4]
            start_seconds = start_time[4:10]
            start_total = float(start_hours)*3600+float(start_minutes)*60+float(start_seconds)

            end_hours = end_time[0:2]
            end_minutes = end_time[2:4]
            end_seconds = end_time[4:10]
            end_total = float(end_hours)*3600+float(end_minutes)*60+float(end_seconds)

            line_time = end_total - start_total

            if len(letters) == 0:
                continue
            increment = line_time/len(words)

            start = start_total
            end = start_total + increment
            for index,word in enumerate(word):
                interval = [start,end]
                intervals.append(interval)
                features.append(letter.encode("utf8"))
                start = end
                end = end+increment

    return intervals,features


def generate_h5py_phones(transcript,destination,video_id):
    intervals,features = align_phones(transcript)
    features_l = [[f] for f in features]
    featuresnp = np.array(features_l,dtype="a8")
    intervalsnp = np.array(intervals)

    data = {}
    data[video_id]={}
    data[video_id]['intervals']=intervalsnp
    data[video_id]['features']=featuresnp

    write5Handle=h5py.File(destination,'w')

    vidHandle=write5Handle.create_group(video_id)
    vidHandle.create_dataset("features",data=data[video_id]["features"])
    vidHandle.create_dataset("intervals",data=data[video_id]["intervals"])
    write5Handle.close()

def generate_h5py_words(transcript,destination,video_id):
    intervals,features = align_words(transcript)
    features_l = [[f] for f in features]
    featuresnp = np.array(features_l,dtype="a8")
    intervalsnp = np.array(intervals)

    data = {}
    data[video_id]={}
    data[video_id]['intervals']=intervalsnp
    data[video_id]['features']=featuresnp

    write5Handle=h5py.File(destination,'w')

    vidHandle=write5Handle.create_group(video_id)
    vidHandle.create_dataset("features",data=data[video_id]["features"])
    vidHandle.create_dataset("intervals",data=data[video_id]["intervals"])
    write5Handle.close()

def read(file):
    f = h5py.File(file, "r")
    dset = f['test']
    print(dset)
    print(dset['features'])
    print(dset['intervals'])
    print(dset['features'][0:10])
    print(dset['intervals'][0:10])
