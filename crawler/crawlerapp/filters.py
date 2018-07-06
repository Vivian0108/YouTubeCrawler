from abc import ABC, abstractmethod
import random
import time, os, subprocess
from crawlerapp.Filters.faceDetectFilter import *
from crawlerapp.Filters.sceneChangeFilter import *
from crawlerapp.definitions import CONFIG_PATH
from crawlerapp.Filters.extractFrames import extractFrames
from django.db import models
from .models import *

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

    @abstractmethod
    def filter(self, video_ids):
        pass

class ExtractFrames(AbstractFilter):
    def name(self):
        return "Extract Frames"
    def description(self):
        return "Extracts the frames from each video. Required before running FaceDetect or SceneChanges"
    def filter(self, video_ids):

        for id in video_ids:
            vid_query = Video.objects.filter(id=id).get()
            try:
                extractFrames(id, 1, vid_query.download_path)
                vid_query.frames_extracted = True
            except:
                print("Failed to extract frames for video " + str(id))
                vid_query.frames_extracted = False
            vid_query.save()
        return []

class AlignFilter(AbstractFilter):
    def name(self):
        return "P2FA Align Video"

    def description(self):
        return "Uses P2FA to align the downloaded videos"

    def filter(self, video_ids):
        my_path = os.path.join(CONFIG_PATH, "downloaded_videos")
        for video in video_ids:
            try:
                video_dir = os.path.join(my_path, video)
                mp4_path = os.path.join(video_dir, video + ".mp4")
                vtt_path = os.path.join(video_dir, video + ".en.vtt")
                plaintext_path = os.path.join(video_dir, video + ".plaintext")
                wav_path = os.path.join(video_dir, video + ".wav")
                pratt_path = os.path.join(video_dir, video + ".pratt")
                output_file = os.path.join(video_dir, video + ".TextGrid")
                align_path = os.path.join(CONFIG_PATH, os.path.join("AZP2FA", os.path.join("p2fa", os.path.join("align.py"))))
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
                subprocess.call("sudo python " + align_path + ' %s %s %s'
                                % (wav_path, plaintext_path, pratt_path),
                                shell=True)
            except FileNotFoundError as e:
                print(e)
        return []

class FaceDetectFilter(AbstractFilter):
    def name(self):
        return "Face Detection"

    def description(self):
        return "Detects Faces. Extract Frames must be run first."

    def filter(self, video_ids):
        downloaded_path = os.path.join(CONFIG_PATH, "downloaded_videos")
        passed = []
        for video in video_ids:
            vid_query = Video.objects.filter(id=video).get()

            try:
                truth_vals = faceDetect(video, downloaded_path)
                if truth_vals[0]:
                    print("Passed " + str(video))
                    vid_query.face_detected = True
                    passed.append(video)
                else:
                    vid_query.face_detected = False
            except:
                print("programming error on video " + str(video))
                vid_query.face_detected = False
            vid_query.save()
        return passed

class SceneChangeFilter(AbstractFilter):
    def name(self):
        return "Scene Change"
    def description(self):
        return "Detects if there are less than 10 scene changes. Extract Frames must be run first."
    def filter(self, video_ids):
        downloaded_path = os.path.join(CONFIG_PATH, "downloaded_videos")
        passed = []
        for video in video_ids:
            vid_query = Video.objects.filter(id=video).get()
            try:
                succeeded = sceneChangeFilter(video, downloaded_path, 25, 100)
                if succeeded:
                    print("Passed " + str(video))
                    vid_query.scene_change_filter_passed = True
                    passed.append(video)
                else:
                    vid_query.scene_change_filter_passed = False
            except:
                print("programming error on video " + str(video))
                vid_query.scene_change_filter_passed = False
        return passed
