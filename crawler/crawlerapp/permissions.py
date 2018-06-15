from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from crawlerapp.models import Job

content_type = ContentType.objects.get_for_model(Job)
permission = Permission.objects.create(
    codename='can_crawl',
    name='Can Crawl and Download',
    content_type=content_type
)
