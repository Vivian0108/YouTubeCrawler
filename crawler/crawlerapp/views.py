from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from .forms import *
from django.views import generic
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
import datetime
from django.contrib.auth.decorators import login_required
from crawlerapp.tasks import crawl_async, download_async
import ast

def home(request):
    return render(request, 'crawlerapp/landing.html')

def all(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')
    jobs = Job.objects.order_by('-id')
    context = {'jobs': jobs}
    return render(request,'crawlerapp/all.html',context)

def dataset_all(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')

    datasets = Dataset.objects.order_by('-id')
    context = {'datasets': datasets}

    return render(request,'crawlerapp/dataset_all.html',context)

def detail(request, job_id):
    if not (request.user.is_authenticated):
        return HttpResponseRedirect('/accounts/login/')
    try:
        job = Job.objects.filter(id=job_id).get()
    except:
        return render(request, 'crawlerapp/jobnotfound.html', {'jobid': job_id})
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
        job.download_started = True
        job.save()
        context['download_started'] = True
        download_async.delay(job_id)
        return redirect('detail', job.id)
    else:
        form = DownloadForm()
        context['form'] = form
        return render(request, 'crawlerapp/detail.html', context)

def dataset_detail(request, dataset_id):
    if not (request.user.is_authenticated):
        return HttpResponseRedirect('/accounts/login/')
    try:
        dataset = Dataset.objects.filter(id=dataset_id).get()
    except:
        return render(request, 'crawlerapp/datasetnotfound.html', {'datasetid': dataset_id})
    #get list of jobs
    job_str_list = ast.literal_eval(dataset.jobs_list)
    job_list = []
    video_sum = 0
    for str_job_id in job_str_list:
        job = Job.objects.filter(id=int(str_job_id)).get()
        job_list.append(job)
        video_sum += int(job.num_vids)
    context = {'dataset_name': dataset.name,
               'dataset_num_vids': video_sum,
               'dataset_num_jobs': len(job_list),
               'dataset_created_date': dataset.created_date,
               'dataset_user_id': dataset.user_id,
               'dataset_id': dataset.id,
               'dataset_jobs': job_list}
    return render(request, 'crawlerapp/dataset_detail.html', context)


def index(request):
    if not (request.user.is_authenticated):
        return HttpResponseRedirect('/accounts/login/')
    jobs = Job.objects.all()
    context = {'jobs': jobs}
    return render(request, 'crawlerapp/index.html', context)

def job_create(request):
    if not (request.user.is_authenticated):
        return HttpResponseRedirect('/accounts/login/')
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
            job.download_started = form.cleaned_data['auto_download']
            job.user_id = request.user.username
            job.save()
            auto_download = job.download_started
            crawl_async.delay(auto_download,str(job.id))
            return redirect('detail', job.id)
    else:
        form = CreateJobForm()

    return render(request, 'crawlerapp/job_create.html', {'form': form})

def dataset_create(request):
    if not (request.user.is_authenticated):
        return HttpResponseRedirect('/accounts/login/')
    if request.method == "POST":
        form = CreateDatasetForm(request.user,request.POST)
        if form.is_valid():
            dataset = Dataset()
            dataset.jobs_list = form.cleaned_data['jobs_list']
            dataset.name = form.cleaned_data['name']
            dataset.description = form.cleaned_data['description']
            dataset.created_date = datetime.datetime.now()
            dataset.user_id = request.user.username
            dataset.save()
            return render(request, 'crawlerapp/landing.html')
    else:
        form = CreateDatasetForm(request.user)

    return render(request, 'crawlerapp/dataset_create.html', {'form': form})

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

def profile(request):
    if not (request.user.is_authenticated):
        return HttpResponseRedirect('/accounts/login/')
    jobs = Job.objects.filter(user_id=request.user.username)
    datasets = Dataset.objects.filter(user_id=request.user.username)
    context = {'jobs': jobs, 'datasets': datasets, 'user': request.user}
    return render(request, 'crawlerapp/profile.html', context)
