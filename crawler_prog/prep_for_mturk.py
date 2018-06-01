import psycopg2
import secrets
import subprocess
import os

CSV_DEST = 'filenames.csv'
URL_DIR = 'videos/'

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
              SELECT video_id, download_path
              FROM video_segment_data 
              WHERE trimmed='true'
             """)
data = cur_.fetchall()

filenames = []
for (video_id, download_path) in data:
    filenames.append(os.path.join(URL_DIR, video_id))
    subprocess.call("cp %s %s" % 
            (os.path.join(download_path, video_id + '_trimmed.mp4'),
                os.path.join(os.path.join('/var/www/html/sqa', URL_DIR))),
            shell=True)

with open(CSV_DEST, 'w') as f:
    f.write('filename\n')
    f.write('\n'.join(filenames))
