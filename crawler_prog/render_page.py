#!/usr/bin/python

from jinja2 import Template
import psycopg2
import secrets
import datetime

template = None
with open('/var/www/html/sqa/crawler-template.html', 'r') as f:
    template = Template(f.read())

try:
    conn_ = psycopg2.connect(
        "dbname='sqa_data'" +
        "user='sqa_downloader' host='localhost' password='" + 
        secrets.DB_PW + "'")
except psycopg2.OperationalError as e:
    print('Unable to connect!\n{0}').format(e)
    sys.exit(1)
cur_ = conn_.cursor()

cur_.execute("SELECT count(distinct(search_term)) FROM youtube_data")
num_search_terms_d_ = cur_.fetchall()[0][0]

cur_.execute("SELECT count(*) FROM youtube_data")
num_rows_ = cur_.fetchall()[0][0]

cur_.execute("SELECT count(video_id) FROM youtube_data WHERE download_time is not null")
videos_d_d_ = cur_.fetchall()[0][0]

cur_.execute("SELECT count(video_id) FROM youtube_data WHERE download_success='false'")
videos_d_f_ = cur_.fetchall()[0][0]

cur_.execute("SELECT count(video_id) FROM youtube_data WHERE face_detect_queue_time is not null")
videos_f_q_ = cur_.fetchall()[0][0]

cur_.execute("SELECT count(video_id) FROM youtube_data WHERE face_detect_success is not null")
videos_f_d_ = cur_.fetchall()[0][0]

cur_.execute("SELECT count(video_id) FROM youtube_data WHERE face_detect_success='true'")
videos_f_a_ = cur_.fetchall()[0][0]

cur_.execute("SELECT count(video_id) FROM youtube_data WHERE p2fa_queue_time is not null")
videos_a_q_ = cur_.fetchall()[0][0]

cur_.execute("SELECT count(video_id) FROM youtube_data WHERE p2fa_success is not null")
videos_a_d_ = cur_.fetchall()[0][0]

cur_.execute("SELECT count(video_id) FROM youtube_data WHERE p2fa_success='true'")
videos_a_a_ = cur_.fetchall()[0][0]

cur_.execute("SELECT count(video_id) FROM youtube_data WHERE punctuation_check_queue_time is not null")
videos_p_q_ = cur_.fetchall()[0][0]

cur_.execute("SELECT count(video_id) FROM youtube_data WHERE punctuation_check_success is not null")
videos_p_d_ = cur_.fetchall()[0][0]

cur_.execute("SELECT count(video_id) FROM youtube_data WHERE punctuation_check_success='true'")
videos_p_a_ = cur_.fetchall()[0][0]

cur_.execute("SELECT count(video_id) FROM youtube_data WHERE punctuation_check_success='true' AND (manual_check is null OR manual_check='true')")
videos_fin_accept_ = cur_.fetchall()[0][0]

with open('/var/www/html/sqa/crawler.html', 'w') as f:
    f.write(template.render(
        time=datetime.datetime.now(),
        num_search_terms_d=num_search_terms_d_,
        num_rows=num_rows_,
        videos_d_d=videos_d_d_,
        videos_d_f=videos_d_f_,
        videos_f_q=videos_f_q_ - videos_f_d_,
        videos_f_d=videos_f_d_,
        videos_f_a=videos_f_a_,
        videos_a_q=videos_a_q_ - videos_a_d_,
        videos_a_d=videos_a_d_,
        videos_a_a=videos_a_a_,
        videos_p_q=videos_p_q_ - videos_p_d_,
        videos_p_d=videos_p_d_,
        videos_p_a=videos_p_a_,
        videos_fin_accept=videos_fin_accept_,
        percentage=str(videos_fin_accept_/30000.0*100),
    ))
