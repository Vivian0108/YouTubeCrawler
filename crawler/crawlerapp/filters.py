from abc import ABC, abstractmethod
import random
import time
import os
import subprocess
import ast
from crawlerapp.Filters.faceDetectFilter import *
from crawlerapp.Filters.sceneChangeFilter import *
from crawlerapp.Filters.ExtractPhones import extractPhones
from crawlerapp.Filters.ExtractWords import extractWords
from crawlerapp.definitions import CONFIG_PATH
from crawlerapp.Filters.extractFrames import extractFrames
from crawlerapp.Filters.NaiveAlign import generate_h5py
from django.db import models
from .models import *
from celery import task
import numpy as np
import h5py
#from AZP2FA.p2fa.align_mod import align


class AbstractFilter(ABC):
    @property
    @abstractmethod
    def name(self):
        return self.name

    @property
    @abstractmethod
    def description(self):
        return self.description

    # Returns a list of strings that are the names of filters that must be run before running
    # the given filter
    @property
    @abstractmethod
    def prefilters(self):
        return self.prefilters

    @abstractmethod
    def filter(self, video_ids):
        pass


class ExtractFrames(AbstractFilter):
    def name(self):
        return "Extract Frames"

    def description(self):
        return "Extracts the frames from each video. Required before running FaceDetect or SceneChanges"

    def prefilters(self):
        return []

    def filter(self, video_ids):
        for id in video_ids:
            vid_query = Video.objects.filter(id=id).get()

            try:
                extractFrames(id, 1, vid_query.download_path)
                print("Extracted " + str(vid_query.id))
                vid_query.filters[self.name()] = True
                vid_query.save()
            except FileExistsError:
                print("Extracted " + str(vid_query.id) + ", file existed")
                vid_query.filters[self.name()] = True
                vid_query.save()
            except Exception as e:
                print("Error extracting frames video " +
                      str(vid_query.id) + ": " + str(e))
                vid_query.filters[self.name()] = False
                vid_query.save()

        return []


class AlignFilter(AbstractFilter):
    def name(self):
        return "P2FA Align Video"

    def description(self):
        return "Uses P2FA to align the downloaded videos"

    def prefilters(self):
        return []

    def filter(self, video_ids):
        my_path = os.path.join(CONFIG_PATH, "downloaded_videos")
        passed = []
        for video in video_ids:
            vid_query = Video.objects.filter(id=video).get()

            #Naive Filter if language isn't english
            if not vid_query.language == 'en':
                try:
                    video_dir = os.path.join(my_path, video)
                    filter_folder_dir = os.path.join(video_dir, "AlignFilter")
                    if not os.path.exists(filter_folder_dir):
                        os.makedirs(filter_folder_dir)
                    lang = "." + str(vid_query.language) + ".vtt"
                    vtt_path = os.path.join(video_dir, video + lang)
                    h5py_file_phones = os.path.join(filter_folder_dir, video + "_phones.hdf5")
                    generate_h5py(vtt_path,h5h5py_file_phones,video)
                    print("Aligned " + str(video))
                    vid_query.filters[self.name()] = True
                    vid_query.save()
                except Exception as e:
                    print("Couldn't extract phones from video " + str(video) + ": " + str(e))
                    vid_query.filters[self.name()] = False
                    vid_query.save()
                continue


            try:
                video_dir = os.path.join(my_path, video)
                filter_folder_dir = os.path.join(video_dir, "AlignFilter")
                if not os.path.exists(filter_folder_dir):
                    os.makedirs(filter_folder_dir)

                # The files that are not generated by this filter stay in the higher level folder
                mp4_path = os.path.join(video_dir, video + ".mp4")
                lang = "." + str(vid_query.language) + ".vtt"
                vtt_path = os.path.join(video_dir, video + lang)
                wav_path = os.path.join(video_dir, video + ".wav")

                plaintext_path = os.path.join(
                    filter_folder_dir, video + ".plaintext")
                pratt_path = os.path.join(filter_folder_dir, video + ".pratt")
                output_file = os.path.join(
                    filter_folder_dir, video + ".TextGrid")
                align_path = os.path.join(CONFIG_PATH, os.path.join(
                    "AZP2FA", os.path.join("p2fa", os.path.join("align.py"))))

                lines = []
                with open(vtt_path, 'r') as f:
                    for line in f:
                        remove_cond = (
                            'WEBVTT' in line or
                            'Kind: captions' in line or
                            'Language: en' in line or
                            '-->' in line
                        )
                        if not remove_cond:
                            lines.append(line.strip())

                with open(plaintext_path, 'w') as f:
                    f.write(' '.join(lines))
                print("Calling p2fa on " + str(video))
                subprocess.call("sudo python " + align_path + ' %s %s %s'
                                % (wav_path, plaintext_path, pratt_path),
                                shell=True)
                try:
                    h5py_file_phones = os.path.join(
                        filter_folder_dir, video + "_phones.hdf5")
                    extractPhones(pratt_path, h5py_file_phones, video)
                    try:
                        h5py_file_words = os.path.join(
                            filter_folder_dir, video + "_words.hdf5")
                        extractWords(pratt_path, h5py_file_words, video)
                        print("Aligned " + str(video))
                        passed.append(video)
                        vid_query.filters[self.name()] = True
                        vid_query.save()
                    except Exception as e:
                        print("Couldn't extract words on video " +
                              video + ": " + str(e))
                        vid_query.filters[self.name()] = False
                        vid_query.save()
                except Exception as e:
                    print("Couldn't extract phones on video " +
                          str(video) + ": " + str(e))
                    vid_query.filters[self.name()] = False
                    vid_query.save()

            except Exception as e:
                print("Error aligning " + str(vid_query.id) + ": " + str(e))
                vid_query.filters[self.name()] = False
                vid_query.save()
        return passed


class FaceDetectFilter(AbstractFilter):
    def name(self):
        return "Face Detection"

    def description(self):
        return "Detects Faces. Extract Frames must be run first."

    def prefilters(self):
        return ["Extract Frames"]

    def filter(self, video_ids):
        downloaded_path = os.path.join(CONFIG_PATH, "downloaded_videos")
        passed = []
        for video in video_ids:
            vid_query = Video.objects.filter(id=video).get()
            try:
                truth_vals = faceDetect(video, downloaded_path)
                if truth_vals[0]:
                    print("Passed " + str(video))
                    passed.append(video)
                    vid_query.filters[self.name()] = True
                else:
                    vid_query.filters[self.name()] = False

            except Exception as e:
                print("Error face detecting video " +
                      str(vid_query.id) + ": " + str(e))
                vid_query.filters[self.name()] = False
            vid_query.save()
        return passed


class SceneChangeFilter(AbstractFilter):
    def name(self):
        return "Scene Change"

    def description(self):
        return "Detects if there are less than 10 scene changes. Extract Frames must be run first."

    def prefilters(self):
        return ["Extract Frames"]

    def filter(self, video_ids):
        downloaded_path = os.path.join(CONFIG_PATH, "downloaded_videos")
        passed = []
        for video in video_ids:
            vid_query = Video.objects.filter(id=video).get()
            try:
                succeeded = sceneChangeFilter(video, downloaded_path, 25, 100)
                if succeeded:
                    print("Passed " + str(video))
                    passed.append(video)
                    vid_query.filters[self.name()] = True
                    vid_query.save()
                else:
                    vid_query.filters[self.name()] = False
                    vid_query.save()
            except Exception as e:
                print("Error scene change detecting video " +
                      str(vid_query.id) + ": " + str(e))
                vid_query.filters[self.name()] = False
                vid_query.save()
        return passed
