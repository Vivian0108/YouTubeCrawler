from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from django.views import generic
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from .forms import *



def form(request):
  return HttpResponse("Hello World!")

def detail(request, job_id):
  return HttpResponse("You're looking at job %s." % job_id)


def index(request):
    jobs = Job.objects.all()
    context = {'jobs': jobs}
    return render(request, 'crawlerapp/index.html', context)

def job_create(request):
  if request.method == "POST":
    form = CreateJobForm(request.POST)
    if form.is_valid():
      job = Job()
      job.language = form.cleaned_data['language']
      job.name = form.cleaned_data['name']
      job.num_vids = form.cleaned_data['num_vids']
      job.save()
      #return render('crawlerapp/detail.html',job.id)
  else:
    form = CreateJobForm()

  return render(request,'crawlerapp/job_create.html',{'form': form})


