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

from apiclient.discovery import build
from apiclient.discovery import HttpError
from oauth2client.tools import argparser

if __name__ == '__main__':
    #SEARCH_TERM_FILE = '/home/edmundtemp/sqa/crawler/search_terms.txt'
    SEARCH_TERM_FILE = 'search_terms.txt'
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
    get_res = '''
                SELECT table_name
    FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
    AND table_schema NOT IN
        ('pg_catalog', 'information_schema');

SELECT column_name
    FROM information_schema.columns
WHERE table_name = 'crawler_data';
    '''
    cur.execute(get_res)
    for r in cur:
        print (r)
