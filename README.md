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

### 1. Clone the repo
### 2. Install Django
Install Django by following the [instructions](https://docs.djangoproject.com/en/2.0/topics/install/#database-installation). 
The crawler is implemented with PostgreSQL. To intall PostgreSQL, which can be downloaded from [here](https://www.postgresql.org/download/). Check [here](https://www.codementor.io/engineerapart/getting-started-with-postgresql-on-mac-osx-are8jcopb) for more information about setting up PostgreSQL database 
For PostgreSQL to function normally, you'll also need to install psycopg2 using `pip3 install psycopg2`. If you only wanna install the package in the virtualenv, call the command after activating the virtualenv (see Step 3 for virtualenv activation). 
### 3. (Optional) [Create a virtual environment for Django](https://docs.djangoproject.com/en/2.1/intro/contributing/)
Activate the virtualenv before continuing to the next steps
```console 
$ source ~/.virtualenvs/[nameOfYourVirtualenv]/bin/activate 
```
### 4. Install the following packages with `pip3 install [packageName]`: 
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
* googletrans (Note: current googletrans might be broken, if so, install through https://stackoverflow.com/questions/52455774/googletrans-stopped-working-with-error-nonetype-object-has-no-attribute-group)
* redis 

### 5. Clean up development remnants: 
Since the cloned repository contains old migraion files from the development process. You should first clean up those migration files to avoid undesirable effects:
```console 
$ find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
$ find . -path "*/migrations/*.pyc"  -delete
```
Then, you need to drop the old `crawler_db` database we created during development. Start the `psql` process on command line: 
```console 
$ psql postgres
```
Then: 
```sql 
postgres=# DROP DATABASE drawler_db 
```
If the database is dropped succesfully, you should get the response `DROP DATABASE`. 

### 6. Create new postgreSQL database and user 
In `psql`, create a new user `username`: 
```sql 
postgres=# CREATE USER username; 
```
If a new user is created correctly, you'll get a `CREATE ROLE` response. 
Create a new database `userdb`: 
```sql 
postgres=# CREATE DATABASE userdb OWNER username; 
```
If a new database is created correctly, you'll get a `CREATE DATABASE` response. 

### 7. Change settings.py 
In settings.py, change the values of both `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` to `redis://localhost:6379`. 
Set the `DATABASES` dictionary to the following value: 
```python 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'username',
        'USER': 'userdb',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5432',
    } 
}
```

### 8. Make new migrations: 
On command line: 
```console 
$ python3 manage.py makemigrations 
$ python3 manage.py migrate 
```
Try running the server: 
```consle 
$ python3 manage.py runserver 
```
Open the brower, go to `localhost:8000`, you should see the YouTubeCrawler homepage. 

## Run Crawler 
### 1. Create a superuser 
A superuser can access the admin site after logging in the account.
Create a superuser on command line: 
```consle 
$ python3 manage.py createsuperuser 
```
Enter the username, email address, and password according to the prompt. 

### 2. Run celery 
On command line, run celery: 
```console 
$ celery -A crawler worker -l info
```

### 3. Run crawler 
Keep the celery running while running the server: 
```console 
$ python3 manage.py runserver 
``` 
Now, you should be able to create a new job on the website. 


## TODO:
- Documentation (setup, etc)
- QA testing
- Get worker2 set up
- Write script to nieave p2fa

Login to postgres with
psql -h localhost userdb -U username

Password:
postgres
