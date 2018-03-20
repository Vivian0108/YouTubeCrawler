#!/usr/bin/python

import sys
import psycopg2
import secrets
import random

try:
    conn_ = psycopg2.connect(
        "dbname='sqa_data'" +
        "user='sqa_downloader' host='localhost' password='" + 
        secrets.DB_PW + "'")
except psycopg2.OperationalError as e:
    print('Unable to connect!\n{0}').format(e)
    sys.exit(1)
cur_ = conn_.cursor()

cur_.execute("SELECT video_id FROM youtube_data WHERE punctuation_check_success='true' and manual_check is null")
video_ids = cur_.fetchall()
video_ids = [vid[0] for vid in video_ids]
random.shuffle(video_ids)
print('\n'.join(video_ids[:int(sys.argv[1])]))
