from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_dashboard, name = 'view_dashboard'),
    path('dashboard', views.view_dashboard, name = 'view_dashboard'),
    path('home', views.view_home, name = 'view_home'),
    path('progress_tracker', views.view_progress, name = 'view_progress'),
    path('create_application', views.create_application, name = 'create_application')
]
