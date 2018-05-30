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
import json
from crawlerapp.download import ex_download

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


def process_search_response(job_id, job_name, query, search_response, client):
    try:
        conn = psycopg2.connect(
            "dbname='crawler_db'" +
            "user='crawler_usr' host='localhost' password='rdGBOx7KSQJmIt6C'")
    except psycopg2.OperationalError as e:
        print('Unable to connect!\n{0}').format(e)
        sys.exit(1)
    cur = conn.cursor()
    conn.autocommit = True
    inserted = 0
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

            try:
                cur.execute('''INSERT INTO crawlerapp_video''' +
                            '''(id,channel_id,query,cc_enabled,language,video_def,video_duration,job_name,job_id,dislike_count,like_count,view_count,comment_count,published_date,search_time,youtube_params)''' +
                            '''VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');''' %
                            (video_id, channel_id, query, captions, default_lang, video_def, video_duration, job_name, job_id, dislike_count, like_count, view_count, comment_count, published_date, datetime.datetime.now(), (json.dumps(vid)).replace("'", "''")))
                conn.commit()
                inserted += 1
            except:
                pass

    try:
        cur.close()
        conn.close()
        return (search_response['nextPageToken'], inserted)
    except KeyError:
        cur.close()
        conn.close()
        return (None,inserted)


def query(terms, job_id):
    conn = psycopg2.connect(
        dbname="crawler_db",
        user="crawler_usr",
        host="localhost",
        password="rdGBOx7KSQJmIt6C")
    cur = conn.cursor()
    conn.autocommit = True

    youtube = build("youtube", "v3",
                    developerKey="AIzaSyC485wtcaeL1yZrciuDWrliKSC74k8UODM")
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
    job_id = ""
    job_name = ""
    channel_id = ""

    for (col, data) in terms:
        if col == 'language':
            if data == '':
                language = 'en'
            else:
                language = data
        elif col == 'num_pages':
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
        elif col == 'channel_id':
            channel_id = data
    page_count = 0
    found_count = 0
    while (nextPageToken or initial):
        if (page_count == int(num_vids)):
            break
        initial = False
        search_response = None
        if (len(channel_id) == 0):
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
        else:
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
                channelId=channel_id,
                # 50 is the maximum allowable value
                maxResults=50,
                pageToken=nextPageToken,
            ).execute()
        if search_response is None:
            break
        cur.execute('''UPDATE crawlerapp_job SET youtube_params = '%s' WHERE id = %s;''' % (
            (json.dumps(search_response)).replace("'", "''"), job_id))

        (nextPageToken, found) = process_search_response(
            job_id, job_name, query, search_response, youtube)
        found_count += found
        cur.execute('''UPDATE crawlerapp_job SET num_vids = '%s' WHERE id = %s;''' % (
            found_count, job_id))
        if nextPageToken:
            page_count += 1
    conn.commit()
    cur.close()
    conn.close()
    return found_count


def ex(auto_download, job_id):
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
    found_count = 0
    found_count = query(zipped_row_data, job_id)
    cur.execute('''UPDATE crawlerapp_job SET num_vids = '%s' WHERE id = %s;''' % (
        found_count, job_id))
    cur.execute(
        '''UPDATE crawlerapp_job SET executed = '%s' WHERE id = %s;''' % (True, job_id))
    conn.commit()

    cur.close()
    conn.close()

    if auto_download:
        ex_download(job_id)
    return found_count


if __name__ == '__main__':
    ex(download_path='downloaded_videos/', job_id="2")
