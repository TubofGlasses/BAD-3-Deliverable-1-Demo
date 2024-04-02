from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_dashboard, name = 'view_dashboard'),
    path('dashboard', views.view_dashboard, name = 'view_dashboard'),
    path('checklist', views.view_checklist, name = 'view_checklist'),
    path('user_profile', views.view_profile, name = 'view_profile'),
    path('create_application', views.create_application, name = 'create_application'),
    path('delete_selected', views.delete_selected, name='delete_selected'),
    path('view_application/<int:pk>/', views.view_application, name='view_application'),
    path('login', views.login, name='login'),
    path('create_account', views.create_account, name = 'create_account'),
    path('delete_account', views.delete_account, name = 'delete_account'),
]
