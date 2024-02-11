from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.view_dashboard, name = 'view_dashboard'),
    path('create_application', views.create_application, name = 'create_application')
]
