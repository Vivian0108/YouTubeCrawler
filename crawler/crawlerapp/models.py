from django.contrib.postgres.fields import JSONField
from django.db import models

# Create your models here.


class Job(models.Model):
    language = models.CharField(max_length=50)
    num_vids = models.IntegerField(default=None, blank=True, null=True)
    num_pages = models.IntegerField(default=None, blank=True, null=True)
    videos = JSONField(default=list)
    name = models.TextField(default="")
    query = models.TextField(default="")
    region = models.TextField(default="")
    created_date = models.DateTimeField(default=None, blank=True, null=True)
    user_id = models.TextField(default="")
    cc_enabled = models.CharField(default="",max_length=50)
    video_def = models.CharField(max_length=15,default="")
    video_duration = models.CharField(max_length=15,default="")
    safe_search = models.CharField(max_length=15,default="")
    ordering = models.CharField(max_length=15,default="")
    executed = models.BooleanField(default=False)
    download_finished = models.BooleanField(default=False)
    download_started = models.BooleanField(default=False)
    channel_id = models.TextField(default="")
    #Format: job.filters[filter_name] = "Applied" or "Active" or None
    filters = JSONField(default=dict)

    # Returns a list of filters than are currently active on this job
    def getActiveFilters(self):
        filter_list = []
        for filter,status in self.filters.items():
            if status == "Active":
                filter_list.append(filter)
        return filter_list

    # Returns a list of filters than have been applied on this job
    def getAppliedFilters(self):
        filter_list = []
        for filter,status in self.filters.items():
            if status == "Applied":
                filter_list.append(filter)
        return filter_list

    class Meta:
        permissions = [('can_crawl',"Can Crawl and Download")]

class Video(models.Model):
    id = models.CharField(max_length=50, default="", primary_key=True)
    channel_id = models.CharField(max_length=50,default="",null=True)
    cc_enabled = models.CharField(max_length=50,default="",null=True)
    #transcript_download_success = models.NullBooleanField()
    language = models.CharField(max_length=15,default="",null=True)
    region = models.CharField(max_length=15,default="",null=True)
    video_def = models.CharField(max_length=15,default="",null=True)
    video_duration = models.CharField(max_length=50,null=True)
    search_time = models.DateTimeField(default=None, blank=True, null=True)
    download_time = models.DateTimeField(default=None, blank=True, null=True)
    download_path = models.TextField(default="",null=True)
    download_success = models.NullBooleanField()
    #Format: video.filters[filter_name] = True if passed or False if failed or None if not tested
    filters = JSONField(default=dict)
    audio_extracted = models.NullBooleanField()
    query = models.TextField(default="",null=True)
    job_ids = JSONField(default=list)
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
