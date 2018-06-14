from django.urls import path
from . import views
from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    # ex: /jobs/
    path('', views.index, name='index'),
    # ex: /jobs/5/
    path('jobs/<int:job_id>/', views.detail, name='detail'),
    path('jobs/new/', views.job_create, name='job-create'),
    path('jobs/all/', views.all,name='all'),
    path('dataset/new/',views.dataset_create,name='dataset-create'),
    path('dataset/<int:dataset_id>/',views.dataset_detail,name='dataset-detail'),
    path('dataset/all/',views.dataset_all,name='dataset-all'),
    path('profile/',views.profile,name='profile'),
    path('mobile/',views.mobile,name='mobile'),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
