from abc import ABC, abstractmethod
import random
import time, os, subprocess
from crawlerapp.Filters.faceDetectFilter import *
from crawlerapp.Filters.sceneChangeFilter import *
from crawlerapp.definitions import CONFIG_PATH
from crawlerapp.Filters.extractFrames import extractFrames
from django.db import models
from .models import *
from celery import task

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

    # Returns function that queries database for the relevant true/false if video has passed filter
    @abstractmethod
    def database_query(self, args, video):
        pass

    @abstractmethod
    def filter(self, video_ids, task):
        pass

class ExtractFrames(AbstractFilter):
    def name(self):
        return "Extract Frames"
    def description(self):
        return "Extracts the frames from each video. Required before running FaceDetect or SceneChanges"
    def prefilters(self):
        return []
    def database_query(self, args, video):
        video.frames_extracted = args
        video.save()

    def filter(self, video_ids, task):
        current = 0
        for id in video_ids:
            task.update_state(
                state='PROGRESS_STATE',
                meta={
                    'video_id': id,
                    'current': current,
                    'total': len(video_ids),
                    'percent': (current//len(video_ids))*100,
                }
            )
            vid_query = Video.objects.filter(id=id).get()
            try:
                extractFrames(id, 1, vid_query.download_path)
                vid_query.frames_extracted = True
                print("Extracted " + str(vid_query.id))
                vid_query.save()
            except Exception as e:
                print("Error extracting frames video " + str(vid_query.id) + ": " + str(e))
                vid_query.frames_extracted = False
                vid_query.save()
            current += 1
        return []

class AlignFilter(AbstractFilter):
    def name(self):
        return "P2FA Align Video"

    def description(self):
        return "Uses P2FA to align the downloaded videos"
    def prefilters(self):
        return []
    def database_query(self, args, video):
        pass
    def filter(self, video_ids, task):
        current = 0
        my_path = os.path.join(CONFIG_PATH, "downloaded_videos")
        for video in video_ids:
            task.update_state(
                state='PROGRESS_STATE',
                meta={
                    'video_id': video,
                    'current': current,
                    'total': len(video_ids),
                }
            )
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
                print("Probably aligned " + str(video))
            except Exception as e:
                print("Error aligning " + str(vid_query.id) + ": " + str(e))
            current += 1
        return []

class FaceDetectFilter(AbstractFilter):
    def name(self):
        return "Face Detection"

    def description(self):
        return "Detects Faces. Extract Frames must be run first."
    def prefilters(self):
        return ["Extract Frames"]
    def database_query(self,args,video):
        video.face_detected = args
        video.save()
    def filter(self, video_ids, task):
        current = 0
        downloaded_path = os.path.join(CONFIG_PATH, "downloaded_videos")
        passed = []
        for video in video_ids:
            task.update_state(
                state='PROGRESS_STATE',
                meta={
                    'video_id': video,
                    'current': current,
                    'total': len(video_ids),
                }
            )
            vid_query = Video.objects.filter(id=video).get()

            try:
                truth_vals = faceDetect(video, downloaded_path)
                if truth_vals[0]:
                    print("Passed " + str(video))
                    vid_query.face_detected = True
                    passed.append(video)
                else:
                    vid_query.face_detected = False
            except Exception as e:
                print("Error face detecting video " + str(vid_query.id) + ": " + str(e))
                vid_query.face_detected = False
            vid_query.save()
            current += 1
        return passed

class SceneChangeFilter(AbstractFilter):
    def name(self):
        return "Scene Change"
    def description(self):
        return "Detects if there are less than 10 scene changes. Extract Frames must be run first."
    def prefilters(self):
        return ["Extract Frames"]
    def database_query(self,args,video):
        video.scene_change_filter_passed = True
        video.save()
    def filter(self, video_ids, task):
        current = 0
        downloaded_path = os.path.join(CONFIG_PATH, "downloaded_videos")
        passed = []
        for video in video_ids:
            task.update_state(
                state='PROGRESS_STATE',
                meta={
                    'video_id': video,
                    'current': current,
                    'total': len(video_ids),
                }
            )
            vid_query = Video.objects.filter(id=video).get()
            try:
                succeeded = sceneChangeFilter(video, downloaded_path, 25, 100)
                if succeeded:
                    print("Passed " + str(video))
                    vid_query.scene_change_filter_passed = True
                    passed.append(video)
                    vid_query.save()
                else:
                    vid_query.scene_change_filter_passed = False
                    vid_query.save()
            except Exception as e:
                print("Error scene change detecting video " + str(vid_query.id) + ": " + str(e))
                vid_query.scene_change_filter_passed = False
                vid_query.save()
            current += 1
        return passed
