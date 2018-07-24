# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from crawlerapp.exec_job import ex
from crawlerapp.download import ex_download
from django.db import models, transaction
from .models import *
import jsonpickle
import ast
from crawlerapp.utils import quit_filter


@shared_task
def crawl_async(job_id):
    ex(job_id)


@shared_task
def download_async(job_id):
    job = Job.objects.filter(id=job_id).get()
    job.download_started = True
    job.save()
    ex_download(job_id)


@shared_task(bind=True)
def filter_async(self, filter, job_id):
    job = Job.objects.filter(id=job_id).get()

    filter_obj = jsonpickle.decode(filter)


    active_filters = job.getActiveFilters()
    if filter_obj.name() not in active_filters:
        job.filters[filter_obj.name()] = "Active"
    job.save()

    downloaded_video_ids = []

    video_ids = job.videos
    for video_id in video_ids:
        video = Video.objects.filter(id=video_id).get()
        if str(video.download_success) == "True":
            downloaded_video_ids.append(video_id)
    video_ids = downloaded_video_ids

    try:
        total_filtered = filter_obj.filter(video_ids)
    except Exception as e:
        total_filtered = []
        print("FILTER FAILED FOR JOB " + str(job.id) + ": " + str(e))

    # Refresh the job before getting the filtered videos
    job = Job.objects.filter(id=job_id).get()


    for video_id in total_filtered:
        vid_query = Video.objects.filter(id=video_id).get()

        vid_query.filters[filter_obj.name()] = True
        vid_query.save()


    job.filters[filter_obj.name()] = "Applied"
    job.save()


@shared_task
def clear_filter_async(filter, job_id):
    filter_obj = jsonpickle.decode(filter)
    filter_name = filter_obj.name()
    job = Job.objects.filter(id=job_id).get()

    videos = job.videos
    for vid in videos:
        vid_query = Video.objects.filter(id=vid).get()
        if vid_query.download_success:
            del vid_query.filters[filter_name]
            vid_query.save()

    del job.filters[filter_name]
    job.save()

    try:
        quit_filter(job_id, filter_name)
    except Exception as e:
        print("Couldn't clear filter: " + str(e))

    job.save()
