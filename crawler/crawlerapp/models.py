from django.db import models

# Create your models here.


class Job(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=50)
    num_vids = models.IntegerField(default=10)
    name = models.TextField(default="")

class Video(models.Model):
	kind = models.TextField(default="")
	etag = models.TextField(default="")
	id = models.TextField(default="",primary_key=True)
	snippet = models.TextField(default="")
	contentDetails = models.TextField(default="")
	status = models.TextField(default="")
	statistics = models.TextField(default="")
	player = models.TextField(default="")
	topicDetails = models.TextField(default="")
	localizations = models.TextField(default="")

class Channel(models.Model):
	kind = models.TextField(default="")
	etag = models.TextField(default="")
	id = models.TextField(default="",primary_key=True)
	snippet = models.TextField(default="")
	contentDetails = models.TextField(default="")
	statistics = models.TextField(default="")
	topicDetails = models.TextField(default="")
	status = models.TextField(default="")
	brandingSettings = models.TextField(default="")
    
