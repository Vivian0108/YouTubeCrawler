from django.shortcuts import render
from crawlerapp.models import *
from crawlerapp.forms import VideoQuestionForm
# Create your views here.
def video_poll(request,video_id):
    video = Video.objects.filter(id=video_id).get()
    if request.method == "POST":
        form = VideoQuestionForm(request.POST)
        if form.is_valid():
            video.questions = form.cleaned_data
            video.save()
        return render(request, 'crawlerapp/landing.html')
    else:
        form = VideoQuestionForm()
    context = {
        'video' : video,
        'form' : form
    }
    return render(request,'DataPoll/videopoll.html',context)
