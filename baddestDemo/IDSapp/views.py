from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Application
from django.core.paginator import Paginator

def view_dashboard(request):
    application_list = Application.objects.all()
    paginator = Paginator(application_list, 10)  # Show 20 applications per page.

    page_number = request.GET.get('page')
    applications = paginator.get_page(page_number)

    return render(request, 'dashboard.html', {'applications': applications})

def view_home(request):
    application_objects = Application.objects.all()
    return render(request, 'home.html', {'applications':application_objects})

def view_progress(request):
    application_objects = Application.objects.all()
    return render(request, 'progress_tracker.html', {'applications':application_objects})

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
            if not expiration_date:
                messages.error(request, 'Expiration date is required.')
                return redirect('create_application')

        if Application.objects.filter(passportNo = passport_no).exists():
            messages.error(request, 'An appllication with this already exists.')
            return redirect('create_application')
        
        # if not first_name:
        #     messages.error(request, 'First name is required.')
        #     return redirect('create_application')
        
        # if not last_name:
        #     messages.error(request, 'Last name is required.')
        #     return redirect('create_application')
        
        # if not nationality:
        #     messages.error(request, 'Nationality is required.')
        #     return redirect('create_application')
        
        # if not company_pos:
        #     messages.error(request, 'Company Position is required.')
        #     return redirect('create_application')
        
        # if not passport_no:
        #     messages.error(request, 'Name is required.')
        #     return redirect('create_application')
        
        # if not application_type:
        #     messages.error(request, 'Name is required.')
        #     return redirect('create_application')
        
        # if not document_type:
        #     messages.error(request, 'Name is required.')
        #     return redirect('create_application')
        
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
