from django.urls import path
from . import views
from django.conf.urls import include, url

urlpatterns = [
    path('', views.home, name='home'),
    # ex: /jobs/
    path('', views.index, name='index'),
    # ex: /jobs/5/
    path('jobs/<int:job_id>/', views.detail, name='detail'),
    path('jobs/new/', views.job_create, name='job-create'),
]
