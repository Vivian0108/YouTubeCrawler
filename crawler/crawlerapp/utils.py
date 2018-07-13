from celery.task.control import inspect, revoke
from celery.result import AsyncResult
import ast
from .models import *
from crawlerapp.filters import *

def quit_filter(job_id, filter_name_str):
    filter_name = 'crawlerapp.filters.' + filter_name_str.replace(' ','')
    # Grab all the current tasks from all the workers
    i = inspect()
    active_list_names = [x for x in i.active()]
    all_tasks = [i.active()[active_list_names[z]] for z in range(len(active_list_names))]
    all_tasks_flatten = [task for sublist in all_tasks for task in sublist]

    for task in all_tasks_flatten:
        # Get the job id
        try:
            if task['name'] == 'crawlerapp.tasks.filter_async':
                args = ast.literal_eval(task['args'])
                task_job_id = args[1]
                if task_job_id == job_id:
                    task_filter_str = args[0]
                    task_filter_name = (ast.literal_eval(task_filter_str))['py/object']
                    if task_filter_name == filter_name:
                        revoke(task['id'], terminate=True)
        except Exception as e:
            print("Failed to quit task " + task['id'])

def job_update(job_id):
    job = Job.objects.filter(id=job_id).get()
    try:
        applied_filters = ast.literal_eval(job.applied_filters)
    except:
        applied_filters = []

    try:
        filtered = ast.literal_eval(job.filtered_videos)
        num_filtered_videos = len(filtered)
    except:
        filtered = []
        num_filtered_videos = 0


    try:
        active_filters = ast.literal_eval(job.active_filters)
    except:
        active_filters = []



    #Creates instances of all filters in filter.py
    gen = (subclass for subclass in AbstractFilter.__subclasses__())
    filters = {}
    for subclass in gen:
        filter_obj = subclass()
        enabled = (not (filter_obj.name() in applied_filters)) and (not (filter_obj.name() in active_filters)) and (len([x for x in filter_obj.prefilters() if x in applied_filters]) == len(filter_obj.prefilters()))
        filters[filter_obj.name()] = {
            'filter_obj': filter_obj,
            'enabled': enabled,
            'num_passed': 0
        }



    downloaded = []
    frames_extracted_list = []
    face_detected_list = []
    scene_change_detected_list = []
    downloaded_query = Video.objects.filter(download_success="True").values()
    for vid in downloaded_query:
        jobs_list = ast.literal_eval(vid['job_ids'])
        if str(job_id) in jobs_list:
            downloaded.append(vid['id'])
            passed_filters = ast.literal_eval(vid['passed_filters'])
            for filter_str in passed_filters:
                filters[filter_str]['num_passed'] += 1
    num_downloaded = len(downloaded)

    try:
        sampled_video = random.sample(filtered, 1)
        sampled_id = sampled_video[0][0]
        url = "https://www.youtube.com/watch?v=" + str(sampled_id)
    except:
        url = "None"


    context = {'job_name': job.name,
               'job_num_vids': job.num_vids,
               'job_videos': job.videos,
               'job_language': job.language,
               'job_channels': job.found_channels,
               'job_query': job.query,
               'job_created_date': str(job.created_date),
               'job_user_id': job.user_id,
               'job_filters': job.filters,
               'cc': job.cc_enabled,
               'executed': job.executed,
               'download_started': job.download_started,
               'download_finished': job.download_finished,
               'job_id': job.id,
               'filters': filters,
               'job_num_filtered_videos': num_filtered_videos,
               'job_applied_filters': applied_filters,
               'num_downloaded': num_downloaded,
               'active_filters': active_filters,
               'sampled_url': url}
    return context
