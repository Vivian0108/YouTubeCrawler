#!/usr/bin/python3
import sys
import os
import shutil
import datetime
from django.utils import timezone
import youtube_dl
import subprocess
import atexit
import json
from django.db import models
from crawlerapp.models import *
import ast
from crawlerapp.download import ex_download
from crawlerapp.tasks import *

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def videos_list_by_id(client, **kwargs):
    # See full sample for function
    #kwargs = remove_empty_kwargs(**kwargs)

    response = client.videos().list(
        **kwargs
    ).execute()

    return response


def process_search_response(job_id, job_name, query, search_response, client, language):
    found = []
    for item in search_response['items']:
        video_id = item['id']['videoId']
        video_data = videos_list_by_id(
            client, part='snippet,contentDetails,statistics', id=video_id)
        for vid in video_data['items']:
            channel_id = vid['snippet']['channelId']
            default_lang = None
            published_date = None
            comment_count = None
            dislike_count = None
            favorite_count = None
            like_count = None
            view_count = None
            captions = None
            video_def = None
            video_duration = None

            try:
                default_lang = vid['snippet']['defaultLanguage']
            except:
                default_lang = language
                #print("Couldn't find defaultLang")
            try:
                default_audio_lang = vid['snipped']['defaultAudioLanguage']
                print(default_audio_lang)
            except:
                print("Can't find defaut audio language")
            try:
                published_date = vid['snippet']['publishedAt']
            except:
                pass
                #print("Couldn't find published date")
            try:
                comment_count = vid['statistics']['commentCount']
            except:
                pass
                #print("Couldn't find comment count")
            try:
                dislike_count = vid['statistics']['dislikeCount']
            except:
                pass
                #print("Couldn't find dislike count")
            try:
                favorite_count = vid['statistics']['favoriteCount']
            except:
                pass
                #print("Couldn't find favorite count")
            try:
                like_count = vid['statistics']['likeCount']
            except:
                pass
                #print("Couldn't find like count")
            try:
                view_count = vid['statistics']['viewCount']
            except:
                pass
                #print("Couldn't find view count")
            try:
                captions = vid['contentDetails']['caption']
            except:
                pass
                #print("Couldn't find captions")
            try:
                video_def = vid['contentDetails']['definition']
            except:
                pass
                #print("Couldn't find definition")
            try:
                video_duration = vid['contentDetails']['duration']

            except:
                pass
                #print("Couldn't find duration")
            if "M" in video_duration:
                video_time = int((video_duration.split('M')[0])[2:])
                if video_time > 10:
                    break
            video,created = Video.objects.get_or_create(id=video_id)
            if created:
                video.channel_id=channel_id
                video.query=query
                video.cc_enabled=captions
                video.language=default_lang
                video.video_def=video_def
                video.video_duration=video_duration
                video.job_ids=[job_id]
                video.dislike_count=dislike_count
                video.like_count=like_count
                video.view_count=view_count
                video.comment_count=comment_count
                video.published_date=published_date
                video.search_time=timezone.now()
                video.frames_extracted=False
                video.save()
            else:
                video.job_ids.append(job_id)
                video.job_ids=list(set(video.job_ids))
                video.save()
            found.append(video_id)

    try:
        return (search_response['nextPageToken'], found)
    except KeyError:
        return (None, found)


def query(job_id):
    job = Job.objects.filter(id=job_id).get()
    youtube = build("youtube", "v3",
                    developerKey="AIzaSyC485wtcaeL1yZrciuDWrliKSC74k8UODM")
    initial = True
    nextPageToken = None

    page_count = 0
    total_found = []
    while (nextPageToken or initial):
        if ((not (job.num_pages is None)) and page_count == int(job.num_pages)):
            break
        initial = False
        search_response = None
        if (len(job.channel_id) == 0):
            search_response = youtube.search().list(
                q=(job.query),
                regionCode = job.region,
                relevanceLanguage=(job.language),
                safeSearch=job.safe_search,
                videoCaption=job.cc_enabled,
                videoDefinition=job.video_def,
                videoDuration=job.video_duration,
                type="video",
                part="id, snippet",
                order=job.ordering,
                # 50 is the maximum allowable value
                maxResults=50,
                pageToken=nextPageToken,
            ).execute()
        else:
            search_response = youtube.search().list(
                q=job.query,
                regionCode = job.region,
                relevanceLanguage=job.language,
                safeSearch=job.safe_search,
                videoCaption=job.cc_enabled,
                videoDefinition=job.video_def,
                videoDuration=job.video_duration,
                type="video",
                part="id, snippet",
                order=job.ordering,
                channelId=job.channel_id,
                # 50 is the maximum allowable value
                maxResults=50,
                pageToken=nextPageToken,
            ).execute()
        if search_response is None:
            break
        (nextPageToken, found) = process_search_response(
            job_id, job.name, job.query, search_response, youtube, job.language, job.region)
        #Refresh job
        job = Job.objects.filter(id=job_id).get()
        total_found.extend(found)
        job.num_vids = len(total_found)
        job.videos = total_found
        job.save()
        if nextPageToken:
            page_count += 1
    return total_found


def ex(job_id):
    job = Job.objects.filter(id=job_id).get()
    total_found = query(job_id)
    job.num_vids = len(total_found)
    job.videos = total_found
    job.executed = True
    job.save()
    ex_download(job_id)
    return total_found
