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
    try:
        video_ids = ast.literal_eval(job.videos)
    except:
        video_ids = []
    filter_obj = jsonpickle.decode(filter)
    filtered = [(vid,filter_obj.name()) for vid in filter_obj.filter(video_ids, download_path)]

    try:
        prefiltered = ast.literal_eval(job.filtered_videos)
    except:
        prefiltered = []
    final_filtered = []
    for video_id,filter_name in filtered:
        #See if we've already gotten this video from another filter
        prefiltered_props = [(id,filters) for (id,filters) in prefiltered if video_id == id]
        if len(prefiltered_props) > 0:
            #if we have, check whether we've run the same filter on it
            (id, filters) = prefiltered_props[0]
            if not (filter_name in filters):
                #If we haven't filtered this video with this filter, add the new filter name
                filters.append(filter_name)
                final_filtered.append((video_id,filters))
                print(final_filtered[-1])
            else:
                #If we have filtered it with this filter, don't check the filter list
                final_filtered.append((video_id,filters))
        else:
            #If we haven't filtered this video before, add it
            final_filtered.append((video_id,[filter_name]))
    final_filtered_ids = [id for (id,filter) in final_filtered]

    final_filtered.extend([(video_id,filters) for (video_id,filters) in prefiltered if video_id not in final_filtered_ids])
    job.filtered_videos = final_filtered

    job.save()
