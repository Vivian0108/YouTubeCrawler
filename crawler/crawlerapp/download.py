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
from crawlerapp.definitions import CONFIG_PATH

from apiclient.discovery import build
from apiclient.discovery import HttpError
from oauth2client.tools import argparser

def download(download_data):
    (download_to_path, video_id) = download_data
    try:
        conn_ = psycopg2.connect(
            "dbname='crawler_db'" +
            "user='crawler_usr' host='localhost' password='" +
            'rdGBOx7KSQJmIt6C' + "'")
    except psycopg2.OperationalError as e:
        print('Unable to connect!\n{0}').format(e)
        sys.exit(1)
    cur_ = conn_.cursor()
    conn_.autocommit = True
    YOUTUBE_BASE_URL = 'https://www.youtube.com/watch?v='
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
            cur_.execute("""
                         UPDATE crawlerapp_video
                         SET download_time='%s',
                             download_success='%s',
                             download_path='%s'
                         WHERE id='%s';
                         """ % (
                datetime.datetime.now(),
                False,
                download_to_path,
                video_id
            )
            )
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
        cur_.execute("""
                     UPDATE crawlerapp_video
                     SET download_time='%s',
                         download_success='%s',
                         download_path='%s'
                     WHERE id='%s';
                     """ % (
            datetime.datetime.now(),
            False,
            download_to_path,
            video_id
        )
        )
    else:
        cur_.execute("""
                     UPDATE crawlerapp_video
                     SET download_time='%s',
                         download_success='%s',
                         download_path='%s'
                     WHERE id='%s';
                     """ % (
            datetime.datetime.now(),
            True,
            download_to_path,
            video_id
        )
        )


def ex_download(job_id):
    try:
        conn = psycopg2.connect(
            "dbname='crawler_db'" +
            "user='crawler_usr' host='localhost' password='" +
            'rdGBOx7KSQJmIt6C' + "'")
    except psycopg2.OperationalError as e:
        print('Unable to connect!\n{0}').format(e)
        sys.exit(1)
    cur = conn.cursor()
    conn.autocommit = True
    cur.execute(
        "SELECT id FROM crawlerapp_video WHERE job_id = '%s';" % (job_id))
    video_ids = [e[0] for e in cur.fetchall()]
#            download_data = [
#                (os.path.join(os.path.join('/media/bighdd5/sqa/', 'downloads'),
#                 video_id),
#                video_id) for video_id in video_ids
#            ]
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
    cur.execute('''UPDATE crawlerapp_job SET download_finished = '%s' WHERE id = '%s' ''' % (True, job_id))
    conn.commit()
    cur.close()
    conn.close()
    #with multiprocessing.Pool(1) as p:
    #    p.map(download, download_data)
        # I added this to stop executing, do we want this? Wasn't here before
        #sys.exit()
