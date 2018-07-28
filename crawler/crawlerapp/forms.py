from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from crawlerapp.generate_models import run_cmds, get_region_snippets
from django.forms.widgets import SelectMultiple
import ast


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
    yt_rawlangs = [('', 'any')] + yt_rawlangs
    language = forms.ChoiceField(choices=yt_rawlangs, required=False)
    language.widget.attrs.update({'class': 'browser-default'})
    yt_rawregions = get_region_snippets()
    yt_rawregions = [('','any')] + yt_rawregions
    region = forms.ChoiceField(choices=yt_rawregions, required=False)
    region.widget.attrs.update({'class': 'browser-default'})
    num_vids = forms.IntegerField(
        help_text="What is the max number of videos you want to crawl (in multiples of 50)? Leave blank for as many as possible.", required=False)
    query = forms.CharField(help_text="What you want youtube to search for")
    channel_id = forms.CharField(
        help_text="Only crawl this channel ID", required=False)
    ordering = forms.ChoiceField(choices=[("relevance", "relevance"), ("date", "date"), ("rating", "rating"), ("title", "title"), ("videoCount", "video count"), ("viewCount", "view count")],
                                 help_text="Select the ordering of the videos")
    ordering.widget.attrs.update({'class': 'browser-default'})
    safe_search = forms.ChoiceField(
        choices=[("none", "none"), ("moderate", "moderate"), ("strict", "strict")])
    safe_search.widget.attrs.update({'class': 'browser-default'})
    cc = forms.ChoiceField(
        choices=[("closedCaption", "closed caption"), ("any", "any"), ("none", "none")])
    cc.widget.attrs.update({'class': 'browser-default'})
    video_def = forms.ChoiceField(
        choices=[("any", "any"), ("high", "high"), ("standard", "standard")])
    video_duration = forms.ChoiceField(choices=[(
        "any", "any"), ("long", "long"), ("medium", "medium"), ("short", "short")])
    video_duration.widget.attrs.update({'class': 'browser-default'})


class CreateDatasetForm(forms.Form):
    name = forms.CharField(help_text="Name your Dataset")
    description = forms.CharField(
        help_text="Describe your Dataset", required=False)
    jobs_list = forms.MultipleChoiceField(
        choices=[])
    jobs = []
    matching_jobs = []

    def __init__(self, user, *args, **kwargs):
        super(CreateDatasetForm, self).__init__(*args, **kwargs)
        jobs = Job.objects.filter(user_id=user.username).values_list(
            'id', 'name').iterator()
        matching_jobs = []
        for job in jobs:
            matching_jobs.append(job)
        self.fields['jobs_list'].choices = matching_jobs

class SelectWithSelected(SelectMultiple):
    """
    Subclass of Django's select widget that allows disabling options.
    To disable an option, pass a dict instead of a string for its label,
    of the form: {'label': 'option label', 'disabled': True}
    """

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        selected = False
        if isinstance(label, dict):
            label, selected = label['label'], label['selected']
        option_dict = super(SelectWithSelected, self).create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if selected:
            option_dict['attrs']['selected'] = 'True'
        return option_dict

class ChangeDatasetJobs(forms.Form):
    jobs_list = forms.MultipleChoiceField(choices=[],required=False)
    jobs_list.widget.attrs.update({'id': 'jobs_list'})
    def __init__(self, user, dataset, *args, **kwargs):
        super(ChangeDatasetJobs, self).__init__(*args, **kwargs)
        jobs = Job.objects.filter(user_id=user.username).values_list(
            'id', 'name')
        preselected = ast.literal_eval(dataset.jobs_list)
        matching_jobs = []
        for job in jobs:
            matching_jobs.append((job[0], {'label': job[1], 'selected': (str(job[0]) in preselected)}))
        self.fields['jobs_list'].widget = SelectWithSelected()
        self.fields['jobs_list'].choices = matching_jobs


class DownloadForm(forms.Form):
    download_path = "downloaded_videos/"
