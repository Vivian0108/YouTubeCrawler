#From http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from kombu import Exchange, Queue

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crawler.settings')

app = Celery('crawler')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


task_routes = {
    'crawler.tasks.*': {'queue': 'celery', 'delivery_mode': 'transient'}
}

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
