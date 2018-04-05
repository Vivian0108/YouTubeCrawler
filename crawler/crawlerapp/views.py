from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from django.views import generic
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from .forms import *
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from crawlerapp.exec_job import ex

def home(request):
    return render(request, 'crawlerapp/landing.html')


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
            job.channel_id = form.cleaned_data['channel_id']
            job.query = form.cleaned_data['query']
            job.location_radius = form.cleaned_data['location_radius']
            job.ordering = form.cleaned_data['ordering']
            job.safe_search = form.cleaned_data['safe_search']
            job.cc_enabled = form.cleaned_data['cc']
            job.video_def = form.cleaned_data['video_def']
            job.video_duration = form.cleaned_data['video_duration']
            job.save()
            print(job.id)
            job.executed = ex(download_path='downloaded_videos/', job_id=str(job.id))

            #return render('crawlerapp/detail.html',job.id)
    else:
        form = CreateJobForm()

    return render(request, 'crawlerapp/job_create.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect(home)
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
