# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from crawlerapp.exec_job import ex
from crawlerapp.download import ex_download
from django.db import models, transaction
from .models import *
import jsonpickle, ast
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
        active_filters.append((filter_obj.name(),0))
        job.active_filters = active_filters
    except:
        active_filters = [(filter_obj.name(),0)]
        job.active_filters = active_filters
    job.save()

    total_filtered = filter_obj.filter(video_ids, job)



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
    try:
        active_filters = ast.literal_eval(job.active_filters)
        active_filters = [(f,p) for f,p in active_filters and f != filter_obj.name()]
        job.active_filters = active_filters
    except:
        pass
    job.save()
    try:
        applied_filters = ast.literal_eval(job.applied_filters)
        if filter_obj.name() not in applied_filters:
            applied_filters.append(filter_obj.name())
        job.applied_filters = applied_filters
    except:
        job.applied_filters = [filter_obj.name()]
    job.save()

@shared_task
def clear_filter_async(filter, job_id):
    filter_obj = jsonpickle.decode(filter)
    filter_name = filter_obj.name()
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

        vid_query = Video.objects.filter(id=video_id).get()
        filter_obj.database_query(args=None,video=vid_query)
    job.filtered_videos = final_filtered
    job.save()
    try:
        applied_filters = ast.literal_eval(job.applied_filters)
        if filter_obj.name() in applied_filters:
            applied_filters.remove(filter_obj.name())
        job.applied_filters = applied_filters
    except:
        pass
    job.save()

    try:
        quit_filter(job_id,filter_name)
    except Exception as e:
        print("Couldn't clear filter: " + str(e))

    try:
        active_filters = ast.literal_eval(job.active_filters)
        active_filters = [(f,p) for f,p in active_filters and f != filter_obj.name()]
        job.active_filters = active_filters
    except:
        pass
    job.save()
