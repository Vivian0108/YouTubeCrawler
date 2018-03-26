from django.db import models

# Create your models here.  
class Job(models.Model):
  created_date = models.DateTimeField(auto_now_add=True)
  language = models.CharField(max_length=50)
  num_vids = models.IntegerField(default=10)
  name = models.TextField(default="")
