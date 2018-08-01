#!/usr/bin/python3
import sys
import os
import shutil
import datetime
import youtube_dl
import subprocess
import atexit
import json
from django.db import models
from crawlerapp.models import *
import ast
from crawlerapp.download import ex_download, download_video
from crawlerapp.tasks import *
from crawlerapp.definitions import CONFIG_PATH

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
    download_state = False
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
                pass
                #print("Couldn't find defaultLang")
            try:
                default_audio_lang = vid['snipped']['defaultAudioLanguage']
            except:
                pass
                #print("Can't find defaut audio language")
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

            video, created = Video.objects.get_or_create(id=video_id)
            if created:
                video.channel_id = channel_id
                video.query = query
                video.cc_enabled = captions
                video.language = default_lang
                video.video_def = video_def
                video.video_duration = video_duration
                video.job_ids = [job_id]
                video.dislike_count = dislike_count
                video.like_count = like_count
                video.view_count = view_count
                video.comment_count = comment_count
                video.published_date = published_date
                video.search_time = datetime.datetime.now()
                video.frames_extracted = False
                video.save()

                # Download to see if we should keep it
                download_data = (os.path.join(os.path.join(
                    CONFIG_PATH, 'downloaded_videos'), video.id), video.id)
                download_state = download_video(download_data, language)

            else:
                video.job_ids.append(job_id)
                video.job_ids = list(set(video.job_ids))
                video.save()
                download_state = True
            found.append(video_id)

    try:
        return (search_response['nextPageToken'], found, download_state)
    except KeyError:
        return (None, found)


def query(job_id):
    job = Job.objects.filter(id=job_id).get()
    youtube = build("youtube", "v3",
                    developerKey="AIzaSyC485wtcaeL1yZrciuDWrliKSC74k8UODM")

    total_found = []
    query_list = str(job.query).split(";")
    current_query = 0
    initial = True
    nextPageToken = None
    page_count = 0

    while (nextPageToken or initial):
        if ((not (job.num_pages is None)) and total_for_query == page_count):
            break
        initial = False
        search_response = None
        if (len(job.channel_id) == 0):
            search_response = youtube.search().list(
                q=query_list[current_query % len(query_list)],
                relevanceLanguage=(job.language),
                safeSearch=job.safe_search,
                videoCaption=job.cc_enabled,
                videoDefinition=job.video_def,
                videoDuration=job.video_duration,
                type="video",
                part="id, snippet",
                order=job.ordering,
                # 50 is the maximum allowable value
                maxResults=1,
                pageToken=nextPageToken,
            ).execute()
        else:
            search_response = youtube.search().list(
                q=query_list[current_query % len(query_list)],
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
                maxResults=1,
                pageToken=nextPageToken,
            ).execute()
        if search_response is None:
            break
        (nextPageToken, found, download_state) = process_search_response(
            job_id, job.name, q, search_response, youtube, job.language)
        # Refresh job
        job = Job.objects.filter(id=job_id).get()
        total_found.extend(found)
        job.num_vids = len(total_found)
        job.videos = total_found
        job.save()
        if nextPageToken and download_state:
            page_count += 1
            current_query +=1
    return total_found


def ex(job_id):
    job = Job.objects.filter(id=job_id).get()
    total_found = query(job_id)
    job.num_vids = len(total_found)
    job.videos = total_found
    job.executed = True
    job.download_finished = True
    job.save()
    # ex_download(job_id)
    return total_found
