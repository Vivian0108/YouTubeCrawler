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
from crawlerapp.download import ex_download, download_video
from crawlerapp.tasks import *
from crawlerapp.definitions import *
from crawlerapp.utils import translate
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def videos_list_by_id(client, **kwargs):
    # See full sample for function
    #kwargs = remove_empty_kwargs(**kwargs)

    response = client.videos().list(
        **kwargs
    ).execute()

    return response


def process_search_response(job_id, job_name, query, search_response, client, language, region):
    found = []
    download_state = False
    job = Job.objects.filter(id=job_id).get()
    for item in search_response['items']:
        video_id = item['id']['videoId']
        job.work_status = "Found video " + str(video_id)
        job.save()
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
                try:
                    video_time = int((video_duration.split('M')[0])[2:])
                except Exception as e:
                    print("Video too long, " + str(e))
                    break
                if video_time > 10:
                    break

            video, created = Video.objects.get_or_create(id=video_id)
            if created:
                job.work_status = str(video_id) + " is new, processing..."
                job.save()
                video.channel_id=channel_id
                video.query=query
                video.cc_enabled=captions
                video.language=default_lang
                video.region=region
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

                # Download to see if we should keep it
                download_data = (os.path.join(CRAWLED_VIDEOS_DIR, video.id), video.id)
                download_state = download_video(download_data, language, job_id)

            else:
                video.job_ids.append(job_id)
                video.job_ids = list(set(video.job_ids))
                video.save()
                if video.language is None or (not (video.language == language)):
                    download_state = False
                else:
                    download_state = video.download_success
            found.append(video_id)

    try:
        return (search_response['nextPageToken'], found, download_state)
    except KeyError:
        return (None, found, download_state)


def query(job_id):
    job = Job.objects.filter(id=job_id).get()
    job.work_status = "Starting crawl..."
    job.save()
    youtube = build("youtube", "v3",
                    developerKey="AIzaSyC485wtcaeL1yZrciuDWrliKSC74k8UODM")

    total_found = []
    query_list = str(job.query).split(";")
    current_query = 0
    initial = True
    nextPageToken = None
    page_count = 0

    while (nextPageToken or initial):
        if ((not (job.num_pages is None)) and job.num_pages == page_count):
            break
        initial = False
        search_response = None
        query_translated = translate(query_list[current_query % len(query_list)], job.language)
        print(query_translated)
        kwargs = {
                'regionCode' : job.region,
                'q':query_translated,
                'relevanceLanguage':(job.language),
                'safeSearch':job.safe_search,
                'videoCaption':job.cc_enabled,
                'videoDefinition':job.video_def,
                'videoDuration':job.video_duration,
                'channelId':job.channel_id,
                'type':"video",
                'part':"id, snippet",
                'order':job.ordering,
                # 50 is the maximum allowable value
                'maxResults':1,
                'pageToken':nextPageToken,
        }
        if len(job.channel_id) == 0:
            del kwargs['channelId']
        if len(job.region) == 0:
            del kwargs['regionCode']
        try:
            search_response = youtube.search().list(**kwargs).execute()
        except Exception as e:
            job.work_status = "Couldn't search: " + str(e)
            job.save()
            search_response = None
        current_query +=1
        if search_response is None:
            break
        try:
            (nextPageToken, found, download_state) = process_search_response(
                job_id, job.name, query_translated, search_response, youtube, job.language,job.region)
            # Refresh job
            job = Job.objects.filter(id=job_id).get()
        except Exception as e:
            # Refresh job
            job = Job.objects.filter(id=job_id).get()
            job.work_status = "Couldn't crawl video: " + str(e)
            job.save()
            nextPageToken = True
            found = []
            download_state = False
        if download_state:
            total_found.extend(found)
        job.num_vids = len(total_found)
        job.videos = total_found
        job.save()
        if nextPageToken and download_state:
            page_count += 1
    return total_found


def ex(job_id):
    job = Job.objects.filter(id=job_id).get()
    total_found = query(job_id)
    job.num_vids = len(total_found)
    job.videos = total_found
    job.executed = True
    job.download_finished = True
    job.work_status = "Finished crawl"
    job.save()
    # ex_download(job_id)
    return total_found
