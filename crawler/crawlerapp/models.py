from django.contrib.postgres.fields import JSONField
from django.db import models

# Create your models here.


class Job(models.Model):
    language = models.CharField(max_length=50)
    num_vids = models.IntegerField(default=None, blank=True, null=True)
    num_pages = models.IntegerField(default=None, blank=True, null=True)
    # videos should be video ids seperated by commas
    videos = models.TextField(default="")
    filtered_videos = models.TextField(default="")
    # channels should be channel ids seperated by commas
    found_channels = models.TextField(default="")
    channel_id = models.CharField(max_length=15,default="")
    name = models.TextField(default="")
    query = models.TextField(default="")
    created_date = models.DateTimeField(default=None, blank=True, null=True)
    user_id = models.TextField(default="")
    # filters should be filter ids seperated by commas
    filters = models.TextField(default="")
    cc_enabled = models.CharField(default="",max_length=50)
    video_def = models.CharField(max_length=15,default="")
    video_duration = models.CharField(max_length=15,default="")
    safe_search = models.CharField(max_length=15,default="")
    ordering = models.CharField(max_length=15,default="")
    executed = models.BooleanField(default=False)
    download_finished = models.BooleanField(default=False)
    download_started = models.BooleanField(default=False)
    active_filters = models.TextField(default="",null=True)
    applied_filters = models.TextField(default="",null=True)

    class Meta:
        permissions = [('can_crawl',"Can Crawl and Download")]

class Video(models.Model):
    id = models.CharField(max_length=50, default="", primary_key=True)
    channel_id = models.CharField(max_length=50,default="",null=True)
    cc_enabled = models.CharField(max_length=50,default="",null=True)
    #transcript_download_success = models.NullBooleanField()
    language = models.CharField(max_length=15,default="",null=True)
    video_def = models.CharField(max_length=15,default="",null=True)
    video_duration = models.CharField(max_length=50,null=True)
    search_time = models.DateTimeField(default=None, blank=True, null=True)
    download_time = models.DateTimeField(default=None, blank=True, null=True)
    download_path = models.TextField(default="",null=True)
    download_success = models.NullBooleanField()
    #frames_extracted = models.NullBooleanField()
    #face_detected = models.NullBooleanField()
    #scene_change_filter_passed = models.NullBooleanField()
    passed_filters = models.TextField(default="",null=True)
    audio_extracted = models.NullBooleanField()
    #mturk_description = models.TextField(default="",null=True)
    #youtube_params = JSONField(default=list,null=True)
    query = models.TextField(default="",null=True)
    job_ids = models.TextField(default="")
    dislike_count = models.CharField(max_length=50,default="",null=True)
    like_count = models.CharField(max_length=50,default="",null=True)
    view_count = models.CharField(max_length=50,default="",null=True)
    comment_count = models.CharField(max_length=50,default="",null=True)
    published_date = models.CharField(max_length=50,default="",null=True)
class Channel(models.Model):
    id = models.CharField(max_length=15,default="",primary_key=True)
    language = models.CharField(max_length=15,default="")
    # videos should be video ids seperated by commas
    videos = models.TextField(default="")
    search_time = models.DateTimeField(default=None, blank=True, null=True)
    owner = models.TextField(default="")
    youtube_params = JSONField(default=list,null=True)
class PlayList(models.Model):
    id = models.CharField(max_length=15,default="",primary_key=True)
    search_time = models.DateTimeField(default=None, blank=True, null=True)
    # videos should be video ids seperated by commas
    videos = models.TextField(default="")
    owner = models.TextField(default="")
    youtube_params = JSONField(default=list,null=True)

class Dataset(models.Model):
    jobs_list = models.TextField(default="")
    name = models.TextField(default="")
    description = models.TextField(default="")
    created_date = models.DateTimeField(default=None, blank=True, null=True)
    user_id = models.TextField(default="")
    filters = models.TextField(default="")
