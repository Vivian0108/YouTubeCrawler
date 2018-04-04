from django.db import models

# Create your models here.


class Job(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=50)
    num_vids = models.IntegerField(default=10)
    name = models.TextField(default="")

class Video(models.Model):
	id = models.CharField(max_length=15,default="",primary_key=True)
    language = models.CharField(max_length=15,default="")
    channel_id = models.CharField(max_length=15,default="")
    cc_enabled = models.BooleanField()
    video_def = models.CharField(max_length=15,default="")
    video_duration = models.DurationField()
    search_time = models.DateTimeField()
    download_time = models.DateTimeField()
    download_path = models.TextField(default="")
    mturk_description = models.TextField(default="")
    youtube_params = models.JSONField(max_length=10000)
    query = models.TextField()

class Channel(models.Model):
	id = models.CharField(max_length=15,default="",primary_key=True)
    language = models.CharField(max_length=15,default="")
    search_time = models.DateTimeField()
    owner = models.TextField()
    youtube_result = models.JSONField(max_length=10000)
