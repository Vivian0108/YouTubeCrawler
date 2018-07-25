# YouTubeCrawler

# Repo Information
This branch contains the Django based webapp for the YouTubeCrawler, created by
Alex Schneidman at Carnegie Mellon University. The crawler/ directory contains
the Django server code. To run the server locally, follow
the setup instructions found in Setup/setup.pdf. Then, run python manage.py runserver
and navigate to localhost:8000 for the site. To run a crawls or filters, celery and
redis must be setup. Make sure to configure the crawler/crawler/settings.py file to ensure
the project configuration matches your machine.

# TODO:
- Add more info to database detail view
- Documentation (setup, etc)
- QA testing
- Order parts for video storage machine
- Add queuing filters option to create job view
- Get worker2 set up
- Logical AND filters?
- Write script that traverses downloaded_videos/, collects relevant hdf5 files, combines into one 
hdf5 file, and downloads to user


# Improvements to Crawling:
- Add list of regions generated from youtube api (crawler/crawlerapp/generate_models.py), pass info to crawler/crawlerapp/forms.py
- Add region option to create job form (crawler/crawlerapp/forms.py) and youtube search api call (crawler/crawlerapp/exec_job.py)
- Once job creation form is submitted, translate query into relevant language before passing to youtube search api
- Merge crawler/crawlerapp/download.py and crawler/crawlerapp/exec_job.py, download transcript of video immediately when
video is crawled, check language of transcript, if correct, download and ffmpeg audio video immediately, if not, throw video out
- Ensure all found transcriptions are downloaded (youtube_dl)
