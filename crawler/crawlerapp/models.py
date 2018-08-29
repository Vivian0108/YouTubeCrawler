from django.contrib.postgres.fields import JSONField
from django.db import models

# Create your models here.


class Job(models.Model):
    #Language requested by client in I18n format, empty if no language specified
    language = models.CharField(max_length=50)

    #Number of videos that have been downloaded, pass language test
    num_vids = models.IntegerField(default=None, blank=True, null=True)

    #Number of videos requested by client
    num_pages = models.IntegerField(default=None, blank=True, null=True)

    #List of video ids that passed the language tests
    videos = JSONField(default=list)

    #Name of Job
    name = models.TextField(default="")

    #Query(ies) specified by client. Multiple queries should be seperated by ;
    query = models.TextField(default="")

    #Region specified by client
    region = models.TextField(default="")

    #Date created
    created_date = models.DateTimeField(default=None, blank=True, null=True)

    #Id of client user
    user_id = models.TextField(default="")

    #Whether client wants closed captions or not (or doesn't care)
    cc_enabled = models.CharField(default="",max_length=50)

    #Client specified video definition
    video_def = models.CharField(max_length=15,default="")

    #Client specified video duration
    video_duration = models.CharField(max_length=15,default="")

    #Client specified safe search setting
    safe_search = models.CharField(max_length=15,default="")

    #Client specified ordering of the videos when they are crawled
    ordering = models.CharField(max_length=15,default="")

    #True iff crawl has finished
    executed = models.BooleanField(default=False)

    #True iff finished downloading
    download_finished = models.BooleanField(default=False)

    #Client specified channel id
    channel_id = models.TextField(default="")

    #Dict of filters this job has encountered
    #Format: job.filters[filter_name] = "Applied" or "Active"
    #If filter_name not in dict, filter has never been ran on this job
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

    # Deletes job and and videos crawled by job if that video only was crawled by this job
    def deleteJob(self):
        videos = list(Video.objects.filter(job_ids__contains=[str(self.id)]))
        for v in videos:
            if len(v.job_ids) > 1:
                v.job_ids.remove(str(self.id))
                v.save()
            else:
                v.delete()
        datasets = list(Dataset.objects.filter(jobs_list__contains=[str(self.id)]))
        for d in datasets:
            d.jobs_list.remove(str(self.id))
            d.save()
        self.delete()

    class Meta:
        permissions = [('can_crawl',"Can Crawl and Download"), ('can_view', "Can Review the passed videos and answer relevant questions")]

class Video(models.Model):
    #Youtube specified unique video id
    id = models.CharField(max_length=50, default="", primary_key=True)

    #Channel of this video
    channel_id = models.CharField(max_length=50,default="",null=True)

    #True iff this video has closed captions available
    cc_enabled = models.CharField(max_length=50,default="",null=True)

    #default_lang of video or language specified by job that crawled this video only
    #if the video had the correct subtitles
    language = models.CharField(max_length=15,default="",null=True)

    #Youtube specified I18n region of the video
    region = models.TextField(default="")

    #Youtube specified max video definition
    video_def = models.CharField(max_length=15,default="",null=True)

    #Video duration in format PTHoursHMinuesMSecondsS
    video_duration = models.CharField(max_length=50,null=True)

    #Time of search
    search_time = models.DateTimeField(default=None, blank=True, null=True)

    #Time when downloaded
    download_time = models.DateTimeField(default=None, blank=True, null=True)

    #Path of .mp4 file
    download_path = models.TextField(default="",null=True)

    #True iff mp4 downloaded, correct language transcription found, and audio extracted
    download_success = models.NullBooleanField()

    #Dict of filters that have been ran/are running on this video
    #Format: video.filters[filter_name] = True if passed or False if failed or None if not tested
    filters = JSONField(default=dict)

    #True iff audio was succesfully extracted
    audio_extracted = models.NullBooleanField()

    #Client specified query that found this job
    query = models.TextField(default="",null=True)

    #List of job ids that have encountered this video
    job_ids = JSONField(default=list)

    #Youtube specified number of dislikes
    dislike_count = models.CharField(max_length=50,default="",null=True)

    #Youtube specified number of likes
    like_count = models.CharField(max_length=50,default="",null=True)

    #Youtube specified number of views
    view_count = models.CharField(max_length=50,default="",null=True)

    #Youtube specified number of comments
    comment_count = models.CharField(max_length=50,default="",null=True)

    #Youtube specified date of publication
    published_date = models.CharField(max_length=50,default="",null=True)



#This model is not currently in use
class Channel(models.Model):
    id = models.CharField(max_length=15,default="",primary_key=True)
    language = models.CharField(max_length=15,default="")
    # videos should be video ids seperated by commas
    videos = models.TextField(default="")
    search_time = models.DateTimeField(default=None, blank=True, null=True)
    owner = models.TextField(default="")
    youtube_params = JSONField(default=list,null=True)

#This model is not currently in use
class PlayList(models.Model):
    id = models.CharField(max_length=15,default="",primary_key=True)
    search_time = models.DateTimeField(default=None, blank=True, null=True)
    # videos should be video ids seperated by commas
    videos = models.TextField(default="")
    owner = models.TextField(default="")
    youtube_params = JSONField(default=list,null=True)

class Dataset(models.Model):
    #List of job ids in this dataset
    jobs_list = JSONField(default=list)

    #Client specified name of dataset
    name = models.TextField(default="")

    #Client specified description of dataset
    description = models.TextField(default="")

    #Date of creation
    created_date = models.DateTimeField(default=None, blank=True, null=True)

    #Id of client user who created dataset
    user_id = models.TextField(default="")

    #Dict of filters that have been applied to underlying jobs (WIP)
    filters = JSONField(default=dict)
