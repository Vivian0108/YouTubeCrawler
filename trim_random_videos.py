import psycopg2
import secrets
import subprocess
import random
import os
from multiprocessing import Pool

NUMBER_OF_VIDEOS = 100

def call(data):
    (command, video_id) = data
    subprocess.call(command, shell=True)
    cur_.execute("""
                  UPDATE video_segment_data 
                  SET trimmed='true' 
                  WHERE video_id='%s'
                 """ % video_id)
    print("Done with %s" % video_id)

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
              SELECT download_path, video_id, 
                     segment_start_secs, segment_end_secs 
              FROM video_segment_data 
              WHERE trimmed is null OR trimmed='false'
             """)
data = cur_.fetchall()

random.shuffle(data)
data = data[:(NUMBER_OF_VIDEOS - 1)]

parameters = []
for (download_path, video_id, start, end) in data:
    start = int(start)
    # ensure that rouding errors don't make the video too short
    duration = int(end - start + 1)
    command = "ffmpeg -loglevel error -ss %s -t %s -i %s -q:v 1 -q:a 1 %s" \
        % (start, duration, os.path.join(download_path, video_id + '.mp4'), 
          os.path.join(download_path, video_id + '_trimmed.mp4'))
    parameters.append((command, video_id))

"""
p = Pool(16)
p.map(call, parameters)
"""
for param in parameters:
    call(param)

