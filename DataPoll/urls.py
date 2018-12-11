from django.urls import path
from . import views
from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('videopoll/<str:video_id>/',views.video_poll,name='video-poll')
]
