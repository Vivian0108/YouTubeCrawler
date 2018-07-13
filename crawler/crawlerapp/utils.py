from celery.task.control import inspect, revoke
from celery.result import AsyncResult
import ast

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
