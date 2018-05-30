from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crawlerapp.generate_models import run_cmds

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(
        max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(
        max_length=254, help_text='Required. Inform a valid email address.')
    andrew = forms.CharField(
        max_length=30, required=False, help_text='Optional.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'password1', 'password2', 'andrew')


class CreateJobForm(forms.Form):
    name = forms.CharField(help_text="Name your job")
    yt_rawlangs = run_cmds()
    yt_rawlangs = [('','any')] + yt_rawlangs
    language = forms.ChoiceField(choices=yt_rawlangs,required=False)
    language.widget.attrs.update({'class': 'browser-default'})
    num_vids = forms.IntegerField(help_text="What is the max number of videos you want to crawl (in multiples of 50)?")
    query = forms.CharField(help_text="What you want youtube to search for")
    channel_id = forms.CharField(help_text="Only crawl this channel ID", required=False)
    ordering = forms.ChoiceField(choices=[("relevance","relevance"),("date","date"),("rating","rating"),("title","title"),("videoCount","video count"),("viewCount","view count")],
                                help_text="Select the ordering of the videos")
    ordering.widget.attrs.update({'class': 'browser-default'})
    safe_search = forms.ChoiceField(choices=[("none","none"),("moderate","moderate"),("strict","strict")])
    safe_search.widget.attrs.update({'class': 'browser-default'})
    cc = forms.ChoiceField(choices=[("any","any"),("closedCaption","closed caption"),("none","none")])
    cc.widget.attrs.update({'class': 'browser-default'})
    video_def = forms.ChoiceField(choices=[("any","any"),("high","high"),("standard","standard")])
    video_duration = forms.ChoiceField(choices=[("any","any"),("long","long"),("medium","medium"),("short","short")])
    video_duration.widget.attrs.update({'class': 'browser-default'})
    auto_download = forms.ChoiceField(choices=[("False","False"),("True","True")])
    auto_download.widget.attrs.update({'class': 'browser-default'})
    def clean_num_vids(self):
        data = self.cleaned_data['num_vids']
        if data < 1:  # need to crawl for at least 1 video
            raise ValidationError(
                _('Invalid number of videos - crawl at least 1 video!'))
        return data

class DownloadForm(forms.Form):
    download_path = "downloaded_videos/"
