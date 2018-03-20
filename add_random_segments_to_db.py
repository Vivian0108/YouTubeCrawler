import psycopg2
import os
from parse_sentences_from_transcript import get_random_segment
import secrets

SECONDS_DESIRED = 120

try:
    conn = psycopg2.connect(
           "dbname='sqa_data'" +
           "user='sqa_downloader' host='localhost' password='" +
           secrets.DB_PW + "'")
except psycopg2.OperationalError as e:
    print('Unable to connect!\n{0}').format(e)
    sys.exit(1)
cur = conn.cursor()
conn.autocommit = True

cur.execute("""
             SELECT video_id, download_path
             FROM youtube_data
             WHERE punctuation_check_success='true' 
             AND (manual_check is null OR manual_check='true')
            """)
video_ids = cur.fetchall()

cur.execute("""
             SELECT video_id
             FROM video_segment_data
            """)
used_video_ids = [vid[0] for vid in cur.fetchall()]

for (video_id, download_path) in video_ids:
    if video_id in used_video_ids:
        continue
    try:
        ((start, end), (seg_start, seg_end)) = \
            get_random_segment(SECONDS_DESIRED, 
                os.path.join(download_path, video_id + '.en.vtt'))
    except:
        print("Failed on %s" % video_id)
        pass
    cur.execute("""
                 INSERT INTO video_segment_data 
                 (video_id, download_path, first_word_secs, 
                 last_word_secs, segment_start_secs, segment_end_secs)
                 VALUES ('%s', '%s', %s, %s, %s, %s)
                """ % 
                (video_id, download_path, start, end, seg_start, seg_end))
    print("Done with %s" % video_id)
