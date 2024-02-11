from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Application

def view_dashboard(request):
    application_objects = Application.objects.all()
    return render(request, 'base.html', {'applications',application_objects})

def create_application(request):
    if (request.method == "POST"):
        first_name = request.POST.get('First_name')
        last_name = request.POST.get('Last_name')
        nationality = request.POST.get('Nationality')
        company_pos = request.POST.get('Company_Pos')
        passport_no = request.POST.get('Passport_no')
        application_type = request.POST.get('Application_type')
        document_type = request.POST.get('Document_type')
        business_unit = request.POST.get('Business_unit')
        status = 'IN_PROGRESS'

        expiration_date = None
        if application_type == 'RENEWAL':
            expiration_date = request.POST.get('Expiration_date')

        if Application.objects.filter(passportNo = passport_no).exists():
            messages.error(request, 'An appllication with this already exists.')
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
            condition = 'ACTIVE',
            expirationDate = expiration_date, 
        )

        new_application.save()
        return redirect('view_dashboard')
    
    return render(request, 'create_application.html')
