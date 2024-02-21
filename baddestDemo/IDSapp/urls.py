from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_dashboard, name = 'view_dashboard'),
    path('dashboard', views.view_dashboard, name = 'view_dashboard'),
    path('checklist', views.view_checklist, name = 'view_checklist'),
    path('progress_tracker', views.view_progress, name = 'view_progress'),
    path('create_application', views.create_application, name = 'create_application')
]
