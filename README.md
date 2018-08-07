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
The crawler is implemented with PostgreSQL. To intall PostgreSQL, which can be downloaded from [here](https://www.postgresql.org/download/). Check [here](https://www.codementor.io/engineerapart/getting-started-with-postgresql-on-mac-osx-are8jcopb) for more information about setting up PostgreSQL database 
For PostgreSQL to function normally, you'll also need to install psycopg2 using `pip3 install psycopg2`. If you only wanna install the package in the virtualenv, call the command after activating the virtualenv (see Step 3 for virtualenv activation). 
#### 3. (Optional) [Create a virtual environment for Django](https://docs.djangoproject.com/en/2.1/intro/contributing/)
Activate the virtualenv before continuing to the next steps
```console 
$ source ~/.virtualenvs/[nameOfYourVirtualenv]/bin/activate 
```
#### 4. Install the following packages with `pip3 install [packageName]`: 
* celery 
* django-celery-results 
* django-celery-beat 
* kombu 
* numpy 
* h5py   
* Pillow
* torch 
* youtube_dl 
* ffmpy 
* apiclient 
* oauth2client 
* google-api-python-client 
* google-auth-oauthlib  
* jsonpickle 
* opencv-python  
* googletrans  

#### 5. Create postgreSQL database and user 

#### 6. Change settings.py 
In settings.py, change the values of both `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` to `redis://localhost:6379`. 
Set the `DATABASES` dictionary to the following value: 
```python 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'crawler_db',
        'USER': 'your database user name',
        'PASSWORD': 'your database password,
        'HOST': 'localhost',
        'PORT': '5432',
    } 
}
```


## Run YouTubeCrawler Locally 


## TODO:
- Documentation (setup, etc)
- QA testing
- Get worker2 set up
- Write script to nieave p2fa
