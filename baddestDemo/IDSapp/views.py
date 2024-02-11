from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Application

def view_dashboard(request):
    application_objects = Application.objects.all()
    return render(request, 'base.html', {'app',application_objects})

def create_application(request):
    if (request.method == "POST"):
        First_name = request.POST.get('First_name')
        Last_name = request.POST.get('Last_name')
        Passport_no = request.POST.get('Passport_no')

        if Application.objects.filter(passportNo = Passport_no).exists():
            messages.error(request, 'An appllication with this already exists.')
            return redirect('create_application')
    return render(request, 'create_application.html')
