from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Application, Account
from django.core.paginator import Paginator
from datetime import datetime
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
import json
import re
from django.contrib.auth import login as django_login, update_session_auth_hash, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError


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
    
    if request.method == 'POST':
        status = request.POST.get('status')
        a.status = status
        a.save()
        return redirect('view_dashboard')
    return render(request, 'view_application.html',{'a':a})



def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        raw_password = request.POST.get('password')

        try:
            account = Account.objects.get(username=username)
            if check_password(raw_password, account.password):
                # Since we're not using Django's built-in User model directly, we need a workaround to log the user in.
                # One approach is to attach the account ID to the session manually (see below).
                # Another approach is to have a corresponding User model instance for each Account and log that User in.
                # Here's an example of the latter:

                # Try to get the corresponding User instance. If it doesn't exist, create one.
                user, created = User.objects.get_or_create(username=account.username)
                if created:
                    user.set_password(raw_password)  # Set a password for the User instance if it's newly created
                    user.save()

                django_login(request, user, backend='django.contrib.auth.backends.ModelBackend')  # Log the user in
                return redirect('view_dashboard')
            else:
                messages.error(request, 'Invalid username or password')
        except Account.DoesNotExist:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')

def create_account(request):
    if request.method == "POST":
        admin_pass = request.POST.get('adminpass')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_pass = request.POST.get('Cpassword')

        # Additional validation and checks...

        # Assuming admin_pass check passes and other validations are ok
        try:
            # Create a User instance
            user = User.objects.create_user(username=username, email=email, password=password)

            # Now you can create the Account instance with a reference to the User instance
            new_account = Account(user=user, username=username, email=email, password=make_password(password))
            new_account.save()
            messages.info(request, 'Account created successfully')
            return redirect('login')
        except IntegrityError as e:
            messages.error(request, 'There was a problem creating the account: ' + str(e))
            return redirect('create_account')

    return render(request, 'create_account.html')

@login_required
def edit_account(request):
    if request.method == "POST":
        new_email = request.POST.get('newEmail')
        current_password = request.POST.get('currentPassword')
        new_password = request.POST.get('newPassword')
        confirm_password = request.POST.get('confirmPassword')

        # Update email if it has changed
        if new_email and new_email != request.user.email:
            request.user.email = new_email
            request.user.save()
            messages.success(request, "Your email has been updated.")

        # Change password
        if current_password and new_password and confirm_password:
            if request.user.check_password(current_password):
                if new_password == confirm_password:
                    request.user.set_password(new_password)
                    request.user.save()
                    # Keep the user logged in after changing the password
                    update_session_auth_hash(request, request.user)
                    messages.success(request, "Your password has been updated.")
                else:
                    messages.error(request, "New passwords do not match.")
            else:
                messages.error(request, "Current password is incorrect.")

        return redirect('edit_account')

    # Pass the user's email to the template to display it
    context = {'user_email': request.user.email}
    return render(request, 'user_profile.html', context)

@login_required
@csrf_protect
def delete_account(request):
    if request.method == "POST":
        input_password = request.POST.get('passIn')
        user = request.user

        if user.check_password(input_password):
            # Delete the related Account instance
            Account.objects.filter(user=user).delete()
            # Delete the User instance
            user.delete()
            messages.success(request, 'Account deleted successfully.')
            logout(request)  # Log out the user after account deletion
            return redirect('login')
        else:
            messages.error(request, 'Incorrect Password.')

    return redirect('edit_account')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')
    
def edit_application(request, pk): #this is only update status for now
    application = get_object_or_404(Application, pk=pk)
    status = request.POST.get('status')
    application.status = status
    application.save()
    return redirect('view_dashboard')