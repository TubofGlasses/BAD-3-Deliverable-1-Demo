from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Application
from django.core.paginator import Paginator
from datetime import datetime
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
import json


def view_dashboard(request):
    application_list = Application.objects.all().order_by('-priority', 'deadline')
    paginator = Paginator(application_list, 10)  # Show 20 applications per page.

    page_number = request.GET.get('page')
    applications = paginator.get_page(page_number)

    return render(request, 'dashboard.html', {'applications': applications})

def view_checklist(request):
    application_objects = Application.objects.all()
    return render(request, 'checklist.html', {'applications':application_objects})

def view_profile(request):
    application_objects = Application.objects.all()
    return render(request, 'progress_tracker.html', {'applications':application_objects})

def create_application(request):
    if (request.method == "POST"):
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        nationality = request.POST.get('nationality')
        company_pos = request.POST.get('position')
        passport_no = request.POST.get('PassNo')
        application_type = request.POST.get('AppType')
        document_type = request.POST.get('docuType')
        business_unit = request.POST.get('businessUnit')
        status = 'In Progress'

        expiration_date = None
        if application_type == 'Renewal':
            expiration_date = request.POST.get('expirationDate')
            
        if expiration_date:
            expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d').date()

        if Application.objects.filter(passportNo=passport_no, documentType=document_type).exists():
            messages.error(request, 'Application with this already exists.')
            return redirect('create_application')
        
        new_application = Application(
            firstName = first_name,
            lastName = last_name,
            nationality = nationality,
            companyPos = company_pos,
            passportNo = passport_no,
            applicationType = application_type,
            documentType = document_type,
            businessUnit = business_unit,
            status = status,
            condition = 'Active',
            expirationDate = expiration_date,  
        )

        new_application.save()
        return redirect('view_dashboard')
    
    context = {
        'status_choices': Application.statuses,
        'conditon_choices': Application.conditions,
        'document_type_choices': Application.document_types,
        'application_type_choices': Application.application_types
    }
    
    return render(request, 'create_application.html', context)

@csrf_protect
def delete_selected(request):
    # This view will now enforce CSRF protection
    data = json.loads(request.body)
    ids_to_delete = data.get('ids', [])
    Application.objects.filter(pk__in=ids_to_delete).delete()
    return JsonResponse({'status': 'success'}, status=200)