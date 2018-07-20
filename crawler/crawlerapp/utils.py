from celery.task.control import inspect, revoke
from celery.result import AsyncResult
import ast
from .models import *
from crawlerapp.filters import *

def quit_filter(job_id, filter_name_str):
    filter_name = 'crawlerapp.filters.' + filter_name_str.replace(' ','')
    # Grab all the current tasks from all the workers
    i = inspect()
    try:
        active_list_names = [x for x in i.active()]
    except:
        print("Couldn't find any workers")
        return
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

def get_celery_worker_status():
    ERROR_KEY = "ERROR"
    try:
        insp = inspect()
        d = insp.stats()
        if not d:
            d = 'No running Celery workers were found.'
    except IOError as e:
        from errno import errorcode
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the Redis server is running.'
        d = msg
    except ImportError as e:
        d = str(e)
    return d

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
        enabled = ((not (filter_obj.name() in applied_filters)) and (not (filter_obj.name() in active_filters))
                    and (len([x for x in filter_obj.prefilters() if x in applied_filters]) == len(filter_obj.prefilters()))
                    and (bool(job.download_finished)))
        progress = -1
        filters[filter_obj.name()] = {
            'filter_obj': filter_obj,
            'enabled': enabled,
            'num_passed': 0,
            'num_failed': 0,
            'progress': progress
        }



    downloaded = []
    frames_extracted_list = []
    face_detected_list = []
    scene_change_detected_list = []
    try:
        job_videos = ast.literal_eval(job.videos)
    except:
        job_videos = []
    for vid in job_videos:
        vid_query = Video.objects.filter(id=vid).get()
        if vid_query.download_success:
            downloaded.append(vid_query.id)
            try:
                passed_filters = ast.literal_eval(vid_query.passed_filters)
            except:
                passed_filters = []
            for filter_str in passed_filters:
                filters[filter_str]['num_passed'] += 1
            try:
                failed_filters = ast.literal_eval(vid_query.passed_filters)
            except:
                failed_filters = []
            for filter_str in failed_filters:
                filters[filter_str]['num_failed'] += 1
    num_downloaded = len(downloaded)

    #Update progress percentage
    for filter_str in filters:
        if filter_str in active_filters:
            progress = (filters[filter_str]['num_passed'] + filters[filter_str]['num_failed'])/(num_downloaded)*100
            filters[filter_str]['progress'] = progress

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
