from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from .forms import *
from django.views import generic
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, permission_required
from crawlerapp.tasks import *
from crawlerapp.filters import *
import jsonpickle, io, ast, csv, os, json, random, datetime
from crawlerapp.definitions import *
from crawlerapp.utils import job_update, get_celery_worker_status
from django.utils import timezone
import tarfile,re

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
    context = job_update(job_id)
    filters = context["filters"]
    if request.method == "POST":
        form = DownloadForm(request.POST)
        if request.POST.get("filter"):
            job = Job.objects.filter(id=job_id).get()

            filter_name = str(request.POST.get("filter"))
            filter_obj = filters[filter_name]["filter_obj"]
            filters[filter_obj.name()]["enabled"] = False

            job.filters[filter_name] = "Active"
            job.save()

            filter_async.delay(jsonpickle.encode(filter_obj), job_id)
        elif request.POST.get("remove"):
            filter_name = str(request.POST.get("remove"))
            filter_obj = filters[filter_name]["filter_obj"]
            #Dont clear the filters asynchronously
            clear_filter_async(jsonpickle.encode(filter_obj), job_id)
        elif request.POST.get("delete_job"):
            job = Job.objects.filter(id=job_id).get()
            job.deleteJob()
            return redirect('all')
        elif request.POST.get("restart_crawl"):
            #Refresh job
            job = Job.objects.filter(id=job_id).get()
            job.executed = False
            job.download_finished = False
            job.work_status = "Restarting crawl..."
            job.save()
            crawl_async.delay(job.id)

        return redirect('detail', job_id)
    else:
        form = DownloadForm()
        context['form'] = form
        return render(request, 'crawlerapp/detail.html', context)

@login_required
@permission_required('crawlerapp.can_crawl', raise_exception=True)
def view_videos(request, job_id):
    face_detected = {}
    job = Job.objects.filter(id=job_id).get()
    for vid in job.videos:
        vid_query = Video.objects.filter(id=vid).get()
        if "Face Detection" in vid_query.filters:
            if vid_query.filters['Face Detection']:
                face_detected[vid] = vid_query
    context = {
        'face_detected': face_detected
    }
    return render(request,'crawlerapp/view_videos.html',context)


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
    try:
        dataset = Dataset.objects.filter(id=dataset_id).get()
    except:
        return render(request, 'crawlerapp/datasetnotfound.html', {'datasetid': dataset_id})
    #get list of jobs
    video_sum = 0
    job_object_list = []
    for job_id in dataset.jobs_list:
        job = Job.objects.filter(id=job_id).get()
        job_object_list.append(job)
        for vid in job.videos:
            vid_query = Video.objects.filter(id=vid).get()
            if vid_query.download_success:
                video_sum += 1
    context = {'dataset_name': dataset.name,
               'dataset_num_vids': video_sum,
               'dataset_num_jobs': len(dataset.jobs_list),
               'dataset_created_date': dataset.created_date,
               'dataset_user_id': dataset.user_id,
               'dataset_id': dataset.id,
               'dataset_jobs': job_object_list}
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
            fieldnames = ['job_id', 'job_name', 'query', 'video_ids']
            writer = csv.DictWriter(response, fieldnames = fieldnames)
            for job in job_list:
                writer.writerow({'job_id': job.id, 'job_name': job.name, 'query': job.query, 'video_ids': job.videos})
            return response
        elif request.POST.get("download_hdf5"):
            p2fa_list = []
            for job_id in dataset.jobs_list:
                job = Job.objects.filter(id=job_id).get()
                for vid in job.videos:
                    vid_query = Video.objects.filter(id=vid).get()
                    if 'P2FA Align Video' in vid_query.filters:
                        if vid_query.filters['P2FA Align Video']:
                            p2fa_list.append(vid_query.id)
            collect.delay(p2fa_list,dataset.id)
            return redirect('dataset-detail', dataset.id)

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
            job.region = form.cleaned_data['region']
            job.name = form.cleaned_data['name']
            job.channel_id = form.cleaned_data['channel_id']
            job.query = form.cleaned_data['query']
            job.ordering = form.cleaned_data['ordering']
            job.safe_search = form.cleaned_data['safe_search']
            job.cc_enabled = form.cleaned_data['cc']
            job.video_def = form.cleaned_data['video_def']
            job.video_duration = form.cleaned_data['video_duration']
            job.created_date = timezone.now()
            job.num_pages = form.cleaned_data['num_vids']
            job.num_vids = 0
            job.user_id = request.user.username
            job.save()
            crawl_async.delay(str(job.id))
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
            dataset.jobs_list = list(form.cleaned_data['jobs_list'])
            dataset.name = form.cleaned_data['name']
            dataset.description = form.cleaned_data['description']
            dataset.created_date = timezone.now()
            dataset.user_id = request.user.username
            dataset.save()
            return redirect('dataset-detail', dataset.id)
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
    jobs = Job.objects.filter(user_id=request.user.username)
    datasets = Dataset.objects.filter(user_id=request.user.username)
    context = {'jobs': jobs, 'datasets': datasets, 'user': request.user}
    return render(request, 'crawlerapp/profile.html', context)


def updateProgress(request, job_id):
    #Can't encode filter object as json, have to get rid of it
    context = job_update(job_id)
    filters = context["filters"]
    for filter_name,filter_dict in filters.items():
        filter_dict["filter_obj"] = None


    return HttpResponse(json.dumps(context), content_type='application/json')

@login_required
def celery_status(request):
    d = get_celery_worker_status()
    context = {'celery_status': d}
    return render(request, 'crawlerapp/celery_status.html', context)

@login_required
def upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        fname = request.FILES['document'].name
        if (form.is_valid() and fname.endswith("tar")):
            doc = form.save()
            with tarfile.open(str(doc.document), "r") as tar:
                all_dirs = [f for f in tar.getmembers() if f.isdir() and f.name.count("/") == 0]
                for member in all_dirs:
                    #Check if we've gotten this video already
                    found = Video.objects.filter(id=str(member.name)).count()
                    if (found > 0):
                        print("Already have " + str(member.name))
                    else:
                        reg_vtt = re.compile(".*.vtt")
                        #If not, check to make sure it's properly formatted
                        all_relevant_files = [f.name for f in tar.getmembers() if f.name.startswith(member.name)]
                        has_mp4 = (member.name + "/" + member.name + ".mp4" in all_relevant_files)
                        has_wav = (member.name + "/" + member.name + ".wav" in all_relevant_files)
                        vtts = list(filter(reg_vtt.match,all_relevant_files))
                        try:
                            lang = vtts[0].split(".")[1]
                        except Exception as e:
                            #Couldn't find a language...
                            continue
                        has_frames = (member.name + "/Frames" in all_relevant_files)
                        has_align = (member.name + "/AlignFilter" in all_relevant_files)
                        if (has_mp4 and has_wav):
                            video = Video(id=str(member.name))
                            video.cc_enabled = True
                            video.language = lang
                            video.search_time = timezone.now()
                            video.audio_extracted = has_wav
                            video.download_success = True
                            video.download_time = timezone.now()
                            video.download_path = os.path.join(CRAWLED_VIDEOS_DIR, member.name)
                            if has_frames:
                                video.filters['Extract Frames'] = True
                            if has_align:
                                video.filters['P2FA Align Video'] = True
                            video.save()
                            tar.extractall(path=CRAWLED_VIDEOS_DIR,members=[f for f in tar.getmembers() if f.name.startswith(member.name)])


            return redirect('home')
    else:
        form = DocumentForm()
    return render(request, 'crawlerapp/upload.html', {
        'form': form
    })
