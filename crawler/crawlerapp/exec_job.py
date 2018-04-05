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

from apiclient.discovery import build
from apiclient.discovery import HttpError
from oauth2client.tools import argparser

def process_search_response(query, search_response):
    try:
        conn = psycopg2.connect(
            "dbname='crawler_db'" +
            "user='crawler_usr' host='localhost' password='rdGBOx7KSQJmIt6C'")
    except psycopg2.OperationalError as e:
        print('Unable to connect!\n{0}').format(e)
        sys.exit(1)
    cur = conn.cursor()
    conn.autocommit = True
    for item in search_response['items']:
        video_id = item['id']['videoId']
        channel_id = (item['snippet']['channelId'])
        print(video_id + ", " + channel_id + ", " + query)
        try:
            cur.execute("INSERT INTO crawlerapp_video" +
                         "(id, channel_id, query)" +
                         "VALUES ('%s', '%s', '%s');" % (video_id, channel_id, query))
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

    for (col, data) in terms:
        if col == 'language':
            language = data
            print (data)
        elif col == 'num_vids':
            num_vids = data
            print (data)
        elif col == 'query':
            query = data
            print (data)
        elif col == 'cc_enabled':
            cc_enabled = data
            print (data)
        elif col == 'video_def':
            video_def = data
            print (data)
        elif col == 'video_duration':
            video_duration = data
            print (data)
        elif col == 'safe_search':
            safe_search = data
            print (data)
        elif col == 'ordering':
            ordering = data
            print (data)
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
        nextPageToken = process_search_response(query, search_response)
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

if __name__ == '__main__':
    run(download_path='downloaded_videos/', job_id="2")
