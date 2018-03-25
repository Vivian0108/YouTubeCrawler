from django.urls import path
from . import views


urlpatterns = [
    path('', views.form, name='form'),
    # ex: /jobs/
    path('', views.index, name='index'),
    # ex: /jobs/5/
    path('jobs/<int:job_id>/', views.detail, name='detail'),
    path('jobs/new/', views.job_create, name='job-create'),
]