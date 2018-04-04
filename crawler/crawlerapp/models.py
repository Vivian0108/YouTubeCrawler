from django.contrib.postgres.fields import JSONField
from django.db import models

# Create your models here.


class Job(models.Model):
    language = models.CharField(max_length=50)
    num_vids = models.IntegerField(default=10)
    # videos should be video ids seperated by commas
    videos = models.TextField(default="")
    # channels should be channel ids seperated by commas
    channels = models.TextField(default="")
    name = models.TextField(default="")
    query = models.TextField(default="")
    created_date = models.DateTimeField(null=True, blank=True)
    user_id = models.TextField(default="")
    # filters should be filter ids seperated by commas
    filters = models.TextField(default="")
    cc_enabled = models.NullBooleanField()
    youtube_params = JSONField()
class Video(models.Model):
    id = models.CharField(max_length=15, default="", primary_key=True)
    channel_id = models.CharField(max_length=15,default="")
    cc_enabled = models.BooleanField()
    transcript_download_success = models.NullBooleanField()
    rating = models.CharField(max_length=100)
    comments = models.TextField(default="")
    language = models.CharField(max_length=15,default="")
    video_def = models.CharField(max_length=15,default="")
    video_duration = models.DurationField(null=True, blank=True)
    search_time = models.DateTimeField(null=True, blank=True)
    download_time = models.DateTimeField(null=True, blank=True)
    download_path = models.TextField(default="")
    download_success = models.NullBooleanField()
    mturk_description = models.TextField(default="")
    youtube_params = JSONField()
    query = models.TextField(default="")
class Channel(models.Model):
    id = models.CharField(max_length=15,default="",primary_key=True)
    language = models.CharField(max_length=15,default="")
    # videos should be video ids seperated by commas
    videos = models.TextField(default="")
    search_time = models.DateTimeField(null=True, blank=True)
    owner = models.TextField(default="")
    youtube_params = JSONField()
class PlayList(models.Model):
    id = models.CharField(max_length=15,default="",primary_key=True)
    search_time = models.DateTimeField(null=True, blank=True)
    # videos should be video ids seperated by commas
    videos = models.TextField(default="")
    owner = models.TextField(default="")
    youtube_params = JSONField()
