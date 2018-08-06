# YouTubeCrawler
Web Address:
[mini.multicomp.cs.cmu.edu](http://mini.multicomp.cs.cmu.edu)
## Repo Information
This branch contains the Django based webapp for the YouTubeCrawler, created by
Alex Schneidman at Carnegie Mellon University. The crawler/ directory contains
the Django server code. To run the server locally, follow
the setup instructions found in Setup/setup.pdf. Then, run python manage.py runserver
and navigate to localhost:8000 for the site. To run a crawls or filters, celery and
redis must be setup. Make sure to configure the crawler/crawler/settings.py file to ensure
the project configuration matches your machine.

## Local Setup 
### Requirements
* Linux 
* Python 3.6 

#### 1. Clone the repo

#### 2. (Optional) [Create a virtual environment for Django](https://docs.djangoproject.com/en/2.1/intro/contributing/)
Activate the virtualenv before continuing to the next steps
```console 
$ source ~/.virtualenvs/[nameOfYourVirtualenv]/bin/activate 
```

#### 3. Install the following packages with `pip3 install [packageName]`: 
* celery 
* kombu
* numpy 
* h5py 
* PIL 
* torch 
* youtube_dl 
* ffmpy 
* apiclient 
* oauth2client
* google 
* google-auth-oauthlib
* jsonpickle 

#### 4. Install the following packages by clicking on the links and following the instructions: 
* [Google API Client](https://developers.google.com/api-client-library/python/start/installation?hl=th) 
* [openCV 3.* ](https://pypi.org/project/opencv-python/) 


(If you're using Python 3.7...) 

## Run YouTubeCrawler Locally 


## TODO:
- Documentation (setup, etc)
- QA testing
- Get worker2 set up
- Write script to nieave p2fa
