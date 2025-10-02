from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("play_proxy/", views.play_proxy, name="play_proxy"),
    path("download_proxy/", views.download_proxy, name="download_proxy"),
    path("download_via_ytdlp/", views.download_via_ytdlp, name="download_via_ytdlp"),
    path('about/', views.about, name='about'),  
    path('contact/', views.contact, name='contact'),  
]
