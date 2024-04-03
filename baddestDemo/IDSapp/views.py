from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Application, Account
from django.core.paginator import Paginator
from datetime import datetime
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
import json
import re
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password


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
    return render(request, 'user_profile.html', {'applications':application_objects})

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

def view_application(request,pk): #add pk here 
    a = get_object_or_404(Application, pk=pk)
    return render(request, 'view_application.html',{'a':a})

def login(request):
    if (request.method == "POST"):
        username = request.POST.get('username')
        password = make_password(request.POST.get('password'))
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect( 'view_dashboard')
        else:
            context = {'error': 'Invalid username or password'}
            return render(request, 'login.html', context)
    
    else:
        return render(request, 'login.html')

def create_account(request):
    if (request.method == "POST"):
        admin_pass = request.POST.get('adminpass')
        user = request.POST.get('username')
        email = request.POST.get('email')
        password = make_password(request.POST.get('password'))
        confirm_pass = make_password(request.POST.get('Cpassword'))
        reg = "(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,}$"
        pat = re.compile(reg)
        mat = re.search(pat, password)

        if Account.objects.filter(email=email).exists():
            messages.error(request, 'There is already an account associated with this email.')
            return redirect('create_account')
        
        if Account.objects.filter(username=user).exists():
            messages.error(request, 'Username is already taken.')
            return redirect('create_account')
        
        if not mat:
            messages.error(request, 'Invalid Password')
            return redirect('create_account')

        if password != confirm_pass:
            messages.error(request, 'Passwords do not match.')
            return redirect('create_account')

        if admin_pass != admin_pass: #placeholder for wherever I will get admin password from
            messages.error(request, 'Admin password provided is incorrect.')
            return redirect('create_account')

        new_account = Account(
            username = user,
            email = email,
            password = password,
        )

        new_account.save()
        messages.info(request, 'Account created successfully')
        return redirect('login')
    
    return render(request, 'create_account.html')

def edit_account(request, pk):
    # Ensure the logged-in user is the account holder
    account = get_object_or_404(Account, pk=pk)
    if request.user != account.user:
        return redirect('view_dashboard')

    if request.method == "POST":
        current_password = request.POST.get('currentPassword')
        new_password = request.POST.get('newPassword')
        confirm_password = request.POST.get('confirmPassword')
        new_email = request.POST.get('newEmail')
        
        # Check if the current password is correct
        if current_password == account.password:
            messages.error(request, "Current password is incorrect.")
            return render(request, 'user_profile.html', {'account': account, 'error': 'current'})
        
        # Check if new password and confirm password match
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return render(request, 'user_profile.html', {'account': account, 'error': 'mismatch'})
        
        # If all checks pass, update the password and possibly other fields
        account.password = make_password(new_password)
        account.save()
        messages.success(request, "Your account has been updated.")
        return redirect('edit_account')  # Redirect to profile or another appropriate page

    # Render the page for a GET request
    return render(request, 'user_profile.html', {'account': account})

@csrf_protect
def delete_account(request, pk):
    Account.objects.filter(pk=pk).delete()
    messages.success(request, 'Account deleted successfully')
    return redirect('login')