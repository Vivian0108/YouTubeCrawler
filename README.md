# YouTubeCrawler
Web Address:
[mini.multicomp.cs.cmu.edu](http://mini.multicomp.cs.cmu.edu)
# Repo Information
This branch contains the Django based webapp for the YouTubeCrawler, created by
Alex Schneidman at Carnegie Mellon University. The crawler/ directory contains
the Django server code. To run the server locally, follow
the setup instructions found in Setup/setup.pdf. Then, run python manage.py runserver
and navigate to localhost:8000 for the site. To run a crawls or filters, celery and
redis must be setup. Make sure to configure the crawler/crawler/settings.py file to ensure
the project configuration matches your machine.

# TODO:
- Documentation (setup, etc)
- QA testing
- Get worker2 set up
- Write script to nieave p2fa
