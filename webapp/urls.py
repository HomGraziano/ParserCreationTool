from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    path('turoparser/', views.turo_parser, name='turo_parser'),
    path('about/', views.about, name='about'),
    path('parsergeneric/', views.parserg, name='parserg'),
    path('download/', views.download_json, name='download_json'),
    path('surprice/', views.surprice, name='surprice'),
    path('vehicleparser/', views.vehicleparser, name='vehicleparser'),
]