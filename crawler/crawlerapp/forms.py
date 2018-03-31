from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


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
    #created_date = models.DateTimeField(auto_now_add=True)
    #language = models.CharField(max_length=50)
    #num_vids = models.IntegerField(default=10)
    #name = models.TextField(default="")
    language = forms.CharField(max_length=50, help_text="Pick a language")
    num_vids = forms.IntegerField(
        help_text="How many videos do you want to crawl?")

    def clean_num_vids(self):
        data = self.cleaned_data['num_vids']
        if data < 1:  # need to crawl for at least 1 video
            raise ValidationError(
                _('Invalid number of videos - crawl at least 1 video!'))
        return data
    name = forms.CharField(help_text="Name your job")
