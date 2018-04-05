#!/usr/bin/python3
import sys
import os
import shutil
import datetime
import youtube_dl
import subprocess
import psycopg2
import atexit
import multiprocessing
import pprint

from apiclient.discovery import build
from apiclient.discovery import HttpError
from oauth2client.tools import argparser

def videos_list_by_id(client, **kwargs):
  # See full sample for function
  #kwargs = remove_empty_kwargs(**kwargs)

  response = client.videos().list(
    **kwargs
  ).execute()

  return response

def process_search_response(job_id, job_name, query, search_response,client):
    try:
        conn = psycopg2.connect(
            "dbname='crawler_db'" +
            "user='crawler_usr' host='localhost' password='rdGBOx7KSQJmIt6C'")
    except psycopg2.OperationalError as e:
        print('Unable to connect!\n{0}').format(e)
        sys.exit(1)
    cur = conn.cursor()
    conn.autocommit = True
    pp = pprint.PrettyPrinter(indent=2)
    for item in search_response['items']:
        video_id = item['id']['videoId']
        video_data = videos_list_by_id(client,part='snippet,contentDetails,statistics',id=video_id)
        for vid in video_data['items']:
            pp.pprint(vid)
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
            try:
                published_date = vid['snippet']['publishedAt']
            except:
                pass
            try:
                comment_count = vid['statistics']['commentCount']
            except:
                pass
            try:
                dislike_count = vid['statistics']['dislikeCount']
            except:
                pass
            try:
                favorite_count = vid['statistics']['favoriteCount']
            except:
                pass
            try:
                like_count = vid['statistics']['likeCount']
            except:
                pass
            try:
                view_count = vid['statistics']['viewCount']
            except:
                pass
            try:
                captions = vid['contentDetails']['caption']
            except:
                pass
            try:
                video_def = vid['contentDetails']['definition']
            except:
                pass
            try:
                video_duration = vid['contentDetails']['duration']
            except:
                pass

            try:
                cur.execute("INSERT INTO crawlerapp_video" +
                             "(id,channel_id,query,cc_enabled,language,video_def,video_duration,job_name,job_id,dislike_count,like_count,view_count,comment_count,published_date,youtube_params)" +
                             "VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" %
                             (video_id,channel_id,query,captions,default_lang,video_def,video_duration,job_name,job_id,dislike_count,like_count,view_count,comment_count,published_date))
            except psycopg2.IntegrityError:
                pass
        try:
            return search_response['nextPageToken']
        except KeyError:
            return None

def query(terms):
    conn = psycopg2.connect(
            dbname="crawler_db",
            user="crawler_usr",
            host="localhost",
            password="rdGBOx7KSQJmIt6C")
    cur = conn.cursor()
    conn.autocommit = True

    youtube = build("youtube", "v3", developerKey="AIzaSyC485wtcaeL1yZrciuDWrliKSC74k8UODM")
    initial = True
    nextPageToken = None

    language = ""
    num_vids = 0
    query = ""
    cc_enabled = ""
    video_def = ""
    video_duration = ""
    safe_search = ""
    ordering = ""
    location_radius = ""
    job_id = ""
    job_name = ""

    for (col, data) in terms:
        if col == 'language':
            language = data
        elif col == 'num_vids':
            num_vids = data
        elif col == 'query':
            query = data
        elif col == 'cc_enabled':
            cc_enabled = data
        elif col == 'video_def':
            video_def = data
        elif col == 'video_duration':
            video_duration = data
        elif col == 'safe_search':
            safe_search = data
        elif col == 'ordering':
            ordering = data
        elif col == 'id':
            job_id = data
        elif col == 'name':
            job_name = data

    video_count = 0
    while (nextPageToken or initial):
        if (video_count == int(num_vids)):
            break
        initial = False
        search_response = youtube.search().list(
            q=query,
            relevanceLanguage=language,
            safeSearch=safe_search,
            videoCaption=cc_enabled,
            videoDefinition=video_def,
            videoDuration=video_duration,
            type="video",
            part="id, snippet",
            order=ordering,
            # 50 is the maximum allowable value
            maxResults=50,
            pageToken=nextPageToken,
        ).execute()
        nextPageToken = process_search_response(job_id, job_name, query, search_response,youtube)
        if nextPageToken:
            video_count += 1

def ex(download_path, job_id):
    conn = psycopg2.connect(
            dbname="crawler_db",
            user="crawler_usr",
            host="localhost",
            password="rdGBOx7KSQJmIt6C")
    cur = conn.cursor()
    conn.autocommit = True

    cur.execute("SELECT * FROM crawlerapp_job WHERE id = " + job_id)
    terms_list = list(cur.fetchall()[0])
    cur.execute('''
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = 'crawlerapp_job';'''
    )
    column_names = [i[0] for i in cur.fetchall()]
    zipped_row_data = list(zip(column_names, terms_list))
    query(zipped_row_data)
    return True
if __name__ == '__main__':
    ex(download_path='downloaded_videos/', job_id="2")
