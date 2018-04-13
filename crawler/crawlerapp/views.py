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
from crawlerapp.download import ex_download
import threading
import datetime


def home(request):
    return render(request, 'crawlerapp/landing.html')


def detail(request, job_id):
    job = Job.objects.filter(id=job_id).get()
    print(job.download_started)
    context = {'job_name': job.name,
               'job_num_vids': job.num_vids,
               'job_videos': job.videos,
               'job_language': job.language,
               'job_channels': job.found_channels,
               'job_query': job.query,
               'job_created_date': job.created_date,
               'job_user_id': job.user_id,
               'job_filters': job.filters,
               'cc': job.cc_enabled,
               'executed': job.executed,
               'download_started': job.download_started,
               'download_finished': job.download_finished,
               'job_id': job.id}
    if request.method == "POST":
        form = DownloadForm(request.POST)
        print("Start download")
        job.download_started = True
        job.save()
        context['download_started'] = True
        download_thread = threading.Thread(
            target=ex_download, args=[job_id])
        download_thread.start()
        return redirect('detail', job.id)
    else:
        form = DownloadForm()
        return render(request, 'crawlerapp/detail.html', context)


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
            job.channel_id = form.cleaned_data['channel_id']
            job.query = form.cleaned_data['query']
            job.ordering = form.cleaned_data['ordering']
            job.safe_search = form.cleaned_data['safe_search']
            job.cc_enabled = form.cleaned_data['cc']
            job.video_def = form.cleaned_data['video_def']
            job.video_duration = form.cleaned_data['video_duration']
            job.created_date = datetime.datetime.now()
            job.num_pages = form.cleaned_data['num_vids']
            job.num_vids = 0
            job.save()
            #vid_count = ex(download_path='downloaded_videos/', job_id=str(job.id))
            #job.num_vids = vid_count
            #job.executed = True
            # job.save()
            job_thread = threading.Thread(
                target=ex, args=('downloaded_videos/', str(job.id)))
            job_thread.start()
            return redirect('detail', job.id)
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
