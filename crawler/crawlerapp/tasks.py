# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from crawlerapp.exec_job import ex
from crawlerapp.download import ex_download
from django.db import models, transaction
from .models import *
import jsonpickle, ast

@shared_task
def crawl_async(job_id):
    ex(job_id)

@shared_task
def download_async(job_id):
    ex_download(job_id)

@shared_task
def filter_async(filter, job_id):
    job = Job.objects.filter(id=job_id).get()
    downloaded_video_ids = []
    try:
        video_ids = ast.literal_eval(job.videos)
        for video_id in video_ids:
            video = Video.objects.filter(id=video_id).get()
            if str(video.download_success) == "True":
                downloaded_video_ids.append(video_id)
        video_ids = downloaded_video_ids
    except:
        video_ids = []

    filter_obj = jsonpickle.decode(filter)
    try:
        active_filters = ast.literal_eval(job.active_filters)
        active_filters.append(filter_obj.name())
        job.active_filters = active_filters
    except:
        active_filters = [filter_obj.name()]
        job.active_filters = active_filters
    job.save()
    print(job.active_filters)



    #start the filter
    total_filtered = filter_obj.filter(video_ids)



    filtered = [(vid,filter_obj.name()) for vid in total_filtered]
    #Refresh the job before getting the filtered videos
    job = Job.objects.filter(id=job_id).get()
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
            else:
                #If we have filtered it with this filter, don't check the filter list
                final_filtered.append((video_id,filters))
        else:
            #If we haven't filtered this video before, add it
            final_filtered.append((video_id,[filter_name]))
    final_filtered_ids = [id for (id,filter) in final_filtered]

    final_filtered.extend([(video_id,filters) for (video_id,filters) in prefiltered if video_id not in final_filtered_ids])
    job.filtered_videos = final_filtered
    print(job.active_filters)
    try:
        active_filters = ast.literal_eval(job.active_filters)
        active_filters.remove(filter_obj.name())
        job.active_filters = active_filters
    except:
        pass
    job.save()
    print(job.active_filters)

@shared_task
def clear_filter_async(filter_name, job_id):
    job = Job.objects.filter(id=job_id).get()
    try:
        filtered_videos = ast.literal_eval(job.filtered_videos)
    except:
        filtered_videos = []
    final_filtered = []
    for (video_id,filters) in filtered_videos:
        if not (filter_name in filters):
            final_filtered.append((video_id,filters))
        elif (filter_name in filters) and (len(filters) > 1):
            filters.remove(filter_name)
            final_filtered.append((video_id,filters))
    job.filtered_videos = final_filtered
    job.save()
