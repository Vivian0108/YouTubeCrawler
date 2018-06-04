# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from crawlerapp.exec_job import ex
from crawlerapp.download import ex_download
from django.db import models
from .models import *
import jsonpickle, ast

@shared_task
def crawl_async(auto_download,job_id):
    ex(auto_download,job_id)

@shared_task
def download_async(job_id):
    ex_download(job_id)

@shared_task
def filter_async(filter, job_id, download_path):
    job = Job.objects.filter(id=job_id).get()
    video_ids = ast.literal_eval(job.videos)
    filter_obj = jsonpickle.decode(filter)
    job.filtered_videos = filter_obj.filter(video_ids, download_path)
    job.save()
