# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from crawlerapp.exec_job import ex
from crawlerapp.download import ex_download

@shared_task
def crawl_async(auto_download,job_id):
    ex(auto_download,job_id)

@shared_task
def download_async(job_id):
    ex_download(job_id)
