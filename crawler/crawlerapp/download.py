#!/usr/bin/python3
import sys
import os, glob
import shutil
import datetime
from django.utils import timezone
import youtube_dl
import subprocess
import atexit
import json, ast
import ffmpy
from crawlerapp.Filters.extractFrames import extractFrames
from crawlerapp.definitions import CONFIG_PATH
from crawlerapp.models import *
from django.db import models

from apiclient.discovery import build
from apiclient.discovery import HttpError
from oauth2client.tools import argparser

def download_video(download_data, requested_lang, job_id):
    job = Job.objects.filter(id=job_id).get()
    (download_to_path, video_id) = download_data
    YOUTUBE_BASE_URL = 'https://www.youtube.com/watch?v='
    # listsubtitles: True   lists all available subtitles
    # allsubtitles: True    downloads all the subtitles of the video
    # subtitleslangs: [langs]   list of languages of the subtitles to download
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'outtmpl': os.path.join(download_to_path, '%(id)s.%(ext)s'),
        'subtitlesformat': 'vtt',
        'writesubtitles': True,
        'format': 'mp4'
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([YOUTUBE_BASE_URL + video_id])
        except:
            job.work_status = "Couldn't download " + str(video_id)
            job.save()
            #Couldn't download...
            return False
    paths = os.listdir(download_to_path)
    subs_and_vid = [False, False]
    if len(requested_lang) == 0:
        lang_path = '.vtt'
    else:
        lang_path = '.' + requested_lang + '.vtt'
    for path in paths:
        if lang_path in path:
            subs_and_vid[0] = True
        if '.mp4' in path:
            subs_and_vid[1] = True
    if not subs_and_vid[1]:
        try:
            shutil.rmtree(download_to_path)
        except FileNotFoundError:
            pass
        video = Video.objects.filter(id=video_id).get()
        video.download_time=datetime.datetime.now()
        video.download_path=download_to_path
        video.download_success=False
        video.save()
        job.work_status = str(video_id) + ": couldn't download video"
        job.save()
        return False
    elif not subs_and_vid[0]:
        try:
            shutil.rmtree(download_to_path)
        except FileNotFoundError:
            pass
        video = Video.objects.filter(id=video_id).get()
        video.download_time=datetime.datetime.now()
        video.download_path=download_to_path
        video.download_success=False
        video.save()
        job.work_status = str(video_id) + ": couldn't download transcription/find correct language"
        job.save()
        return False
    else:
        video = Video.objects.filter(id=video_id).get()
        video.download_time=datetime.datetime.now()
        video.download_path=download_to_path
        video.download_success=True

        job.work_status = str(video_id) + ": download successful, extracting audio"
        job.save()

        if video.language is None:
            video.language = requested_lang
            if (len(video.language) == 0):
                all = glob.glob(os.path.join(download_to_path,"*.vtt"))
                video.language = all[0].split(".")[1]

        input = os.path.join(video.download_path, video_id + ".mp4")
        output = os.path.join(video.download_path, video_id + ".wav")
        try:
            ff = ffmpy.FFmpeg(
                inputs={input: None},
                outputs={output: '-ar 11025 -ac 1 -s s16 -b:a 176k'}
            )
            ff.run()
            video.audio_extracted = True
        except FileExistsError:
            print("Audio already extracted")
            video.audio_extracted = True
        except Exception as e:
            print("Failed to extract audio for " + str(video.id) + ": " + str(e))
            job.work_status = str(video_id) + ": couldn't extract audio"
            job.save()
            video.audio_extracted = False
        video.save()
        job.work_status = str(video_id) + ": succesfully downloaded"
        job.save()
        return True
    return True


def download(download_data):
    (download_to_path, video_id) = download_data
    YOUTUBE_BASE_URL = 'https://www.youtube.com/watch?v='
    # listsubtitles: True   lists all available subtitles
    # allsubtitles: True    downloads all the subtitles of the video
    # subtitleslangs: [langs]   list of languages of the subtitles to download
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'outtmpl': os.path.join(download_to_path, '%(id)s.%(ext)s'),
        'subtitlesformat': 'vtt',
        'writesubtitles': True,
        'format': 'mp4'
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([YOUTUBE_BASE_URL + video_id])
        except:
            video = Video.objects.filter(id=video_id).get()
            video.download_time=timezone.now()
            video.download_path=download_to_path
            video.download_success=False
            video.save()
            return
    paths = os.listdir(download_to_path)
    subs_and_vid = [False, False]
    for path in paths:
        if '.en.vtt' in path:
            subs_and_vid[0] = True
        if '.mp4' in path:
            subs_and_vid[1] = True
    if not(subs_and_vid[0] and subs_and_vid[1]):
        try:
            shutil.rmtree(download_to_path)
        except FileNotFoundError:
            pass
        video = Video.objects.filter(id=video_id).get()
        video.download_time=timezone.now()
        video.download_path=download_to_path
        video.download_success=False
        video.save()
    else:
        video = Video.objects.filter(id=video_id).get()
        video.download_time=timezone.now()
        video.download_path=download_to_path
        video.download_success=True
        input = os.path.join(video.download_path, video_id + ".mp4")
        output = os.path.join(video.download_path, video_id + ".wav")
        try:
            ff = ffmpy.FFmpeg(
                inputs={input: None},
                outputs={output: '-ar 11025 -ac 1 -s s16 -b:a 176k'}
            )
            ff.run()
            video.audio_extracted = True
        except:
            print("Failed to extract audio for " + str(video.id))
            video.audio_extracted = False
        video.save()

def ex_download(job_id):
    job = Job.objects.filter(id=job_id).get()
    video_ids = job.videos
    download_data = [(os.path.join(os.path.join(
        (CONFIG_PATH), 'downloaded_videos'), video_id), video_id) for video_id in video_ids]
    num_download = len(download_data)
    # Code to restrict number downloaded, if you want
    if (len(sys.argv) == 3):
        num_download = int(sys.argv[2])
    download_data = download_data[0:num_download]
    #Downloads videos sequentially, python doesnt like downloading them in parallel in another thread
    for data in download_data:
        download(data)
    job.download_finished = True
    job.save()
