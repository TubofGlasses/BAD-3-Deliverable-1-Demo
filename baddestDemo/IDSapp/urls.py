from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_dashboard, name = 'view_dashboard'),
    path('dashboard', views.view_dashboard, name = 'view_dashboard'),
    path('checklist', views.view_checklist, name = 'view_checklist'),
    path('user_profile', views.view_profile, name = 'view_profile'),
    path('create_application', views.create_application, name = 'create_application')
]
