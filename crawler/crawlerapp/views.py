from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from .forms import *
from django.views import generic
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
import datetime
from django.contrib.auth.decorators import login_required, permission_required
from crawlerapp.tasks import *
from crawlerapp.filters import *
import jsonpickle, io, ast, csv

def home(request):
    return render(request, 'crawlerapp/landing.html')

def mobile(request):
    return render(request, 'crawlerapp/mobile.html')

@login_required
@permission_required('crawlerapp.can_crawl', raise_exception=True)
def all(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')
    jobs = Job.objects.order_by('-id')
    context = {'jobs': jobs}
    return render(request,'crawlerapp/all.html',context)


@login_required
@permission_required('crawlerapp.can_crawl', raise_exception=True)
def dataset_all(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')

    datasets = Dataset.objects.order_by('-id')
    context = {'datasets': datasets}

    return render(request,'crawlerapp/dataset_all.html',context)


@login_required
@permission_required('crawlerapp.can_crawl', raise_exception=True)
def detail(request, job_id):
    if not (request.user.is_authenticated):
        return HttpResponseRedirect('/accounts/login/')
    try:
        job = Job.objects.filter(id=job_id).get()
    except:
        return render(request, 'crawlerapp/jobnotfound.html', {'jobid': job_id})
    #Creates instances of all filters in filter.py
    gen = (subclass for subclass in AbstractFilter.__subclasses__())
    filters = []
    index = 0
    for subclass in gen:
        filters.append((subclass(), index))
        index += 1
    num_filtered_videos = 0
    applied_filters = []
    try:
        filtered = ast.literal_eval(job.filtered_videos)
        num_filtered_videos = len(filtered)
        for (video_id,applied) in filtered:
            for f in applied:
                if f not in applied_filters:
                    applied_filters.append(f)
    except:
        pass
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
               'job_id': job.id,
               'filters': filters,
               'job_num_filtered_videos': num_filtered_videos,
               'job_applied_filters': applied_filters}
    if request.method == "POST":
        form = DownloadForm(request.POST)
        if request.POST.get("download"):
            job.download_started = True
            job.save()
            context['download_started'] = True
            download_async.delay(job_id)
        elif request.POST.get("filter"):
            filter_num = int(request.POST.get("filter"))
            filter_obj = filters[filter_num][0]
            filter_async.delay(jsonpickle.encode(filter_obj), job_id, "")
        elif request.POST.get("remove"):
            filter_num = int(request.POST.get("remove"))
            filter_name = filters[filter_num][0].name()
            #Dont clear the filters asynchronously
            clear_filter_async(filter_name, job_id)
        return redirect('detail', job.id)
    else:
        form = DownloadForm()
        context['form'] = form
        return render(request, 'crawlerapp/detail.html', context)

def newcsv(data, csvheader, fieldnames):
    """
    Create a new csv file that represents generated data.
    """
    csvrow = []
    new_csvfile = io.StringIO()
    wr = csv.writer(new_csvfile, quoting=csv.QUOTE_ALL)
    wr.writerow([csvheader])
    wr = csv.DictWriter(new_csvfile, fieldnames = fieldnames)

    for job in data:
        wr.writerow(job.videos)

    return new_csvfile


@login_required
@permission_required('crawlerapp.can_crawl', raise_exception=True)
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
    if request.method == "POST":
        if request.POST.get("submit_jobs"):
            form = ChangeDatasetJobs(request.user,dataset,request.POST)
            if form.is_valid():
                dataset.jobs_list = form.cleaned_data['jobs_list']
                dataset.save()
                return redirect('dataset-detail', dataset.id)
        elif request.POST.get("download"):
            # Create the HttpResponse object with the appropriate CSV header.
            #redir_url = 'crawlerapp/dataset/' + str(dataset.id)
            #response = HttpResponseRedirect('',content_type='text/csv')
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=' + dataset.name + '.csv'
            fieldnames = ['job_id', 'job_name', 'video_ids']
            writer = csv.DictWriter(response, fieldnames = fieldnames)
            for job in job_list:
                writer.writerow({'job_id': job.id, 'job_name': job.name, 'video_ids': job.videos})
            return response

    else:
        form = ChangeDatasetJobs(request.user,dataset)
        context['form'] = form
        return render(request, 'crawlerapp/dataset_detail.html', context)


def index(request):
    if not (request.user.is_authenticated):
        return HttpResponseRedirect('/accounts/login/')
    jobs = Job.objects.all()
    context = {'jobs': jobs}
    return render(request, 'crawlerapp/index.html', context)


@login_required
@permission_required('crawlerapp.can_crawl', raise_exception=True)
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


@login_required
@permission_required('crawlerapp.can_crawl', raise_exception=True)
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


@login_required
def profile(request):
    if not (request.user.is_authenticated):
        return HttpResponseRedirect('/accounts/login/')
    jobs = Job.objects.filter(user_id=request.user.username)
    datasets = Dataset.objects.filter(user_id=request.user.username)
    context = {'jobs': jobs, 'datasets': datasets, 'user': request.user}
    return render(request, 'crawlerapp/profile.html', context)
