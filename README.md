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
#### 2. Install Django
Install Django by following the [instructions](https://docs.djangoproject.com/en/2.0/topics/install/#database-installation). 
The crawler is implemented with PostgreSQL. To intall PostgreSQL, which can be downloaded from [here](https://www.postgresql.org/download/). 
For PostgreSQL to function normally, you'll also need to install psycopg2 using `pip3 install psycopg2`. If you only wanna install the package in the virtualenv, call the command after activating the virtualenv (see Step 3 for virtualenv activation). 
#### 3. (Optional) [Create a virtual environment for Django](https://docs.djangoproject.com/en/2.1/intro/contributing/)
Activate the virtualenv before continuing to the next steps
```console 
$ source ~/.virtualenvs/[nameOfYourVirtualenv]/bin/activate 
```
#### 4. Install the following packages with `pip3 install [packageName]`: 
* celery (check) 
* django-celery-results (check) 
* django-celery-beat (c) 
* kombu
* numpy 
* h5py 
* PIL 
* torch 
* youtube_dl (c) 
* ffmpy (c)
* apiclient 
* oauth2client
* google-api-python-client (c) 
* google-auth-oauthlib (c) 
* jsonpickle 
* opencv-python (c) 
#### 4. Install the following packages by clicking on the links and following the instructions: 
* [Google API Client](https://developers.google.com/api-client-library/python/start/installation?hl=th) 
* [openCV 3.* ](https://pypi.org/project/opencv-python/) 


## Run YouTubeCrawler Locally 


## TODO:
- Documentation (setup, etc)
- QA testing
- Get worker2 set up
- Write script to nieave p2fa
