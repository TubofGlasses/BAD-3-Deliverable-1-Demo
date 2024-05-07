from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name = 'login'),
    path('dashboard', views.view_dashboard, name = 'view_dashboard'),
    path('checklist', views.view_checklist, name = 'view_checklist'),
    path('user_profile', views.edit_account, name = 'edit_account'),
    path('create_application', views.create_application, name = 'create_application'),
    path('create_another', views.create_another, name = 'create_another'),
    path('delete_selected', views.delete_selected, name='delete_selected'),
    path('view_application/<int:pk>/', views.view_application, name='view_application'),
    path('login', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create_account', views.create_account, name = 'create_account'),
    path('delete_account', views.delete_account, name = 'delete_account'),
    path('edit_application/<int:pk>/', views.edit_application, name = 'edit_application'),
    path('create_checklist', views.create_checklist, name='create_checklist'),
    path('update_checklist/<int:checklist_id>/', views.update_checklist, name='update_checklist'),
    path('delete/<int:checklist_id>/', views.delete_checklist, name='delete_checklist'),
    path('dashboard/<value>', views.filter, name = 'filter'),
    path('search', views.search, name ='search')
]
