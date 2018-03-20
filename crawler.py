#!/usr/bin/python3

from AZP2FA.p2fa.align_mod import align
import secrets
import sys
import os
import shutil
import datetime
import youtube_dl
import subprocess
import psycopg2
import atexit
import multiprocessing
from definitions import CONFIG_PATH

from apiclient.discovery import build
from apiclient.discovery import HttpError
from oauth2client.tools import argparser

def process_search_response(video_ids, term, search_response):
    try:
        conn_ = psycopg2.connect(
            "dbname='sqa_data'" +
            "user='sqa_downloader' host='localhost' password='" +
            secrets.DB_PW + "'")
    except psycopg2.OperationalError as e:
        print('Unable to connect!\n{0}').format(e)
        sys.exit(1)
    cur_ = conn_.cursor()
    conn_.autocommit = True
    for item in search_response['items']:
        video_id = item['id']['videoId']
        if video_id in video_ids:
            continue
        channel_id = (item['snippet']['channelId'])
        try:
            cur_.execute("INSERT INTO youtube_data" +
                         "(video_id, channel_id, search_term)" +
                         "VALUES ('%s', '%s', '%s');" % (video_id, channel_id, term))
        except psycopg2.IntegrityError:
            pass
    try:
        return search_response['nextPageToken']
    except KeyError:
        return None

def query(term):
    try:
        conn_ = psycopg2.connect(
            "dbname='sqa_data'" +
            "user='sqa_downloader' host='localhost' password='" +
            secrets.DB_PW + "'")
    except psycopg2.OperationalError as e:
        print('Unable to connect!\n{0}').format(e)
        sys.exit(1)
    cur_ = conn_.cursor()
    conn_.autocommit = True
    youtube = build("youtube", "v3", developerKey=secrets.DEVELOPER_KEY)
    initial = True
    nextPageToken = None
    while (nextPageToken or initial):
        initial = False
        search_response = youtube.search().list(
            q=term,
            relevanceLanguage="en",
            safeSearch="strict",
            videoCaption="closedCaption",
            videoDefinition="high",
            videoDuration="short",
            type="video",
            part="id, snippet",
            order="viewCount",
            # 50 is the maximum allowable value
            maxResults=50,
            pageToken=nextPageToken,
        ).execute()
        cur_.execute("SELECT video_id FROM youtube_data;")
        #Note, used to be cur.fetchall(), why?
        #video_ids = [e[0] for e in cur.fetchall()]
        video_ids = [e[0] for e in cur_.fetchall()]
        print ("Video ids: " + str(video_ids))
        #Send search results to postgresql server and get the next page to be seached (nextPageToken)
        #Continues until we can't find another page
        nextPageToken = process_search_response(
                video_ids, term, search_response
            )

def download(download_data):
    (download_to_path, video_id) = download_data
    try:
        conn_ = psycopg2.connect(
            "dbname='sqa_data'" +
            "user='sqa_downloader' host='localhost' password='" +
            secrets.DB_PW + "'")
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
                         UPDATE youtube_data
                         SET download_time='%s',
                             download_success='%s',
                             download_path='%s'
                         WHERE video_id='%s';
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
                     UPDATE youtube_data
                     SET download_time='%s',
                         download_success='%s',
                         download_path='%s'
                     WHERE video_id='%s';
                     """ % (
                             datetime.datetime.now(),
                             False,
                             download_to_path,
                             video_id
                         )
                    )
    else:
        cur_.execute("""
                     UPDATE youtube_data
                     SET download_time='%s',
                         download_success='%s',
                         download_path='%s'
                     WHERE video_id='%s';
                     """ % (
                             datetime.datetime.now(),
                             True,
                             download_to_path,
                             video_id
                         )
                     )

def face_detect_video(face_detect_data):
    try:
        conn_ = psycopg2.connect(
            "dbname='sqa_data'" +
            "user='sqa_downloader' host='localhost' password='" +
            secrets.DB_PW + "'")
    except psycopg2.OperationalError as e:
        print('Unable to connect!\n{0}').format(e)
        sys.exit(1)
    cur_ = conn_.cursor()
    conn_.autocommit = True
    PERCENT_THRESHOLD = 40
    (download_path, video_id) = face_detect_data
    try:
        out = subprocess.check_output(
                './face_detector %s sqa 0 0 24' % (
                    download_path + '.mp4'
                ), shell=True)
    except subprocess.CalledProcessError:
        cur_.execute("""
                     UPDATE youtube_data
                     SET face_detect_attempt_time='%s',
                         face_detect_percent='%s',
                         face_detect_success='%s'
                     WHERE video_id='%s';
                     """ % (
                             datetime.datetime.now(),
                             -1,
                             False,
                             video_id
                         )
                     )
        return
    percentage = int(out)
    if percentage < PERCENT_THRESHOLD:
        try:
            shutil.rmtree(download_path)
        except FileNotFoundError:
            pass
    cur_.execute("""
                 UPDATE youtube_data
                 SET face_detect_attempt_time='%s',
                     face_detect_percent='%s',
                     face_detect_success='%s'
                 WHERE video_id='%s';
                 """ % (
                         datetime.datetime.now(),
                         percentage,
                         percentage >= PERCENT_THRESHOLD,
                         video_id
                     )
                 )

def align_video(align_data):
    (download_path, video_id) = align_data
    path = download_path
    try:
    #    conn_ = psycopg2.connect(
    #        "dbname='sqa_data'" +
    #        "user='sqa_downloader' host='localhost' password='" +
    #        secrets.DB_PW + "'")
        conn_ = psycopg2.connect(
            dbname="sqa_data",
            user="sqa_downloader",
            host="localhost",
            password=secrets.DB_PW)
    except psycopg2.OperationalError as e:
        print('Unable to connect!\n{0}').format(e)
        sys.exit(1)
    cur_ = conn_.cursor()
    conn_.autocommit = True
    cur_.execute("""
                 UPDATE youtube_data
                 SET p2fa_attempt_time='%s'
                 WHERE video_id='%s';
                 """ % (
                         datetime.datetime.now(),
                         video_id
                     )
                 )
    subprocess.call('ffmpeg -y -loglevel quiet -i %s %s' %
            (path + '.mp4', path + '.wav'),
            shell=True)

    lines = []
    with open(path + '.en.vtt', 'r') as f:
        for line in f:
            remove_cond = (
                    'WEBVTT' in line or
                    'Kind: captions' in line or
                    'Language: en' in line or
                    '-->' in line
                )
            if not remove_cond:
                lines.append(line.strip())

    with open(path + '.plaintext', 'w') as f:
        f.write(' '.join(lines))

    subprocess.call('/home/edmundtemp/sqa/crawler/AZP2FA/p2fa/align.py %s %s %s'
        % (path + '.wav', path + '.plaintext', path + '.pratt'),
        shell=True)

    if check_pratt(path + '.pratt'):
        cur_.execute("""
                     UPDATE youtube_data
                     SET p2fa_success='%s'
                     WHERE video_id='%s';
                     """ % (
                             True,
                             video_id
                         )
                     )
    else:
        cur_.execute("""
                     UPDATE youtube_data
                     SET p2fa_success='%s'
                     WHERE video_id='%s';
                     """ % (
                             False,
                             video_id
                         )
                     )

def check_pratt(pratt_file):
    if not os.path.isfile(pratt_file):
        return False
    lines = []
    with open(pratt_file, 'r') as f:
        lines = f.read().split('\n')
    first_space = 0
    for i in range(len(lines)):
        if 'sp' == lines[i]:
            first_space = i
            break
    lines = lines[first_space - 2:]
    word_timing = []
    space_timing = []
    accumulator = 0
    for i in range(int(len(lines) / 3)):
        start = float(lines[i * 3])
        stop = float(lines[i * 3 + 1])
        phoneme = float(lines[i * 3 + 2])
        if phoneme == 'sp':
            accumulator = 0
            space_timing.append(stop - start)
            word_timing.append(accumulator)
        else:
            accumulator += stop - start

    for time in word_timing:
        if time > 3:
            return False
    for time in space_timing:
        if time > 5:
            return False
    return True

def punctuation_check(punc_data):
    (download_path, video_id) = punc_data
    path = download_path
    try:
        conn_ = psycopg2.connect(
            "dbname='sqa_data'" +
            "user='sqa_downloader' host='localhost' password='" +
            secrets.DB_PW + "'")
    except psycopg2.OperationalError as e:
        print('Unable to connect!\n{0}').format(e)
        sys.exit(1)
    cur_ = conn_.cursor()
    conn_.autocommit = True
    cur_.execute("""
                 UPDATE youtube_data
                 SET punctuation_check_attempt_time='%s'
                 WHERE video_id='%s';
                 """ % (
                         datetime.datetime.now(),
                         video_id
                     )
                 )
    with open(path + '.plaintext', 'r') as f:
        for c in f.read():
            if c == ',' or c == '!' or c == '.' or c == '?' or c == ';':
                cur_.execute("""
                             UPDATE youtube_data
                             SET punctuation_check_success='%s'
                             WHERE video_id='%s';
                             """ % (
                                     True,
                                     video_id
                                 )
                             )
                return True
    cur_.execute("""
                 UPDATE youtube_data
                 SET punctuation_check_success='%s'
                 WHERE video_id='%s';
                 """ % (
                         False,
                         video_id
                     )
                 )

def random_cut(video_id, length):
    print("hi")

def stop():
    conn = None
    try:
        conn = psycopg2.connect(
            "dbname='sqa_data'" +
            "user='sqa_downloader' host='localhost' password='" +
            secrets.DB_PW + "'");
    except psycopg2.OperationalError as e:
        print('Unable to connect!\n{0}').format(e)
        sys.exit(1)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("INSERT INTO crawler_data VALUES (DEFAULT, DEFAULT, false);")
    cur.close()

atexit.register(stop)
if __name__ == '__main__':
    #SEARCH_TERM_FILE = '/home/edmundtemp/sqa/crawler/search_terms.txt'
    SEARCH_TERM_FILE = 'search_terms.txt'
    DOWNLOAD_PATH = 'downloaded_videos/'
    conn = None
    try:
    #    conn = psycopg2.connect(
    #        "dbname='sqa_data'" +
    #        "user='sqa_downloader' host='localhost' password='temp'" +
    #        secrets.DB_PW + "'")
        conn = psycopg2.connect(
            dbname="sqa_data",
            user="sqa_downloader",
            host="localhost",
            password=secrets.DB_PW)
    except psycopg2.OperationalError as e:
        print('Unable to connect!\n{0}').format(e)
        sys.exit(1)
    cur = conn.cursor()
    conn.autocommit = True
    cur.execute("INSERT INTO crawler_data VALUES (DEFAULT, DEFAULT, true);")

    while (True):
        if sys.argv[1] == 'search':
            with open(SEARCH_TERM_FILE, 'r') as f:
                for term in f:
                    term = term.strip()
                    #Make sure not repeating queries
                    cur.execute("SELECT DISTINCT search_term FROM youtube_data;")
                    terms = [e[0] for e in cur.fetchall()]
                    if term not in terms:
                        print ("Querying " + term)
                        query(term)
        elif sys.argv[1] == 'download':
            cur.execute("SELECT video_id FROM youtube_data WHERE download_time is NULL;")
            video_ids = [e[0] for e in cur.fetchall()]
#            download_data = [
#                (os.path.join(os.path.join('/media/bighdd5/sqa/', 'downloads'),
#                 video_id),
#                video_id) for video_id in video_ids
#            ]
            download_data = [(os.path.join(os.path.join((CONFIG_PATH), 'downloaded_videos'),video_id),video_id) for video_id in video_ids]
            print (len(download_data))
            num_download = len(download_data)
            #Code to restrict number downloaded, if you want
            if (len(sys.argv) == 3):
                num_download = int(sys.argv[2])
            download_data = download_data[0:num_download]
            print (len(download_data))
            with multiprocessing.Pool(4) as p:
                p.map(download, download_data)
                #I added this to stop executing, do we want this? Wasn't here before
                sys.exit()
        elif sys.argv[1] == 'face_detect':
            cur.execute("""
                    SELECT video_id, download_path FROM youtube_data WHERE
                    download_success = 'true' AND face_detect_queue_time is null;
                    """)
            face_detect_data = [(e[0], e[1]) for e in cur.fetchall()]
            for (video_id, _) in face_detect_data:
                cur.execute("""
                            UPDATE youtube_data
                            SET face_detect_queue_time='%s'
                            WHERE video_id='%s';
                            """ % (
                                    datetime.datetime.now(),
                                    video_id
                                )
                            )
            face_detect_data = [
                (
                    os.path.join(download_path, video_id),
                    video_id
                ) for (video_id, download_path) in face_detect_data
            ]
            with multiprocessing.Pool(16) as p:
                p.map(face_detect_video, face_detect_data)

        elif sys.argv[1] == 'p2fa':
            cur.execute("""
                    SELECT video_id, download_path FROM youtube_data WHERE
                    download_success = 'true'
                    AND face_detect_success = 'true'
                    AND p2fa_queue_time is null;
                    """)
            align_data = [(e[0], e[1]) for e in cur.fetchall()]
            for (video_id, _) in align_data:
                cur.execute("""
                             UPDATE youtube_data
                             SET p2fa_queue_time='%s'
                             WHERE video_id='%s';
                             """ % (
                                     datetime.datetime.now(),
                                     video_id
                                 )
                             )
            align_data = [
                (
                    os.path.join(download_path, video_id),
                    video_id
                ) for (video_id, download_path) in align_data
            ]
            with multiprocessing.Pool(4) as p:
                p.map(align_video, align_data)

        elif sys.argv[1] == 'punc':
            cur.execute("""
                    SELECT video_id, download_path FROM youtube_data WHERE
                    download_success = 'true'
                    AND face_detect_success = 'true'
                    AND p2fa_success = 'true';
                    """)
            punc_data = [(e[0], e[1]) for e in cur.fetchall()]
            for (video_id, _) in punc_data:
                cur.execute("""
                             UPDATE youtube_data
                             SET punctuation_check_queue_time='%s'
                             WHERE video_id='%s';
                             """ % (
                                     datetime.datetime.now(),
                                     video_id
                                 )
                             )
            punc_data = [
                (
                    os.path.join(download_path, video_id),
                    video_id
                ) for (video_id, download_path) in punc_data
            ]
            with multiprocessing.Pool(4) as p:
                p.map(punctuation_check, punc_data)

    cur.close()
