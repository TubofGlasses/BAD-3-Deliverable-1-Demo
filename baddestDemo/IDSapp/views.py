from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Application, ApplicationArchive, DeletedApplication, Account, Checklist, ChecklistItem
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
            messages.error(request, 'Application already exists.')
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

def create_another(request):
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
        return redirect('create_application')
    

@csrf_protect
def delete_selected(request):
    # This view will now enforce CSRF protection
    data = json.loads(request.body)
    ids_to_delete = data.get('ids', [])
    
    for i in ids_to_delete:
        application = get_object_or_404(Application, pk=i)
        first_name = application.getFirstName()
        last_name = application.getLastName()
        nationality = application.getNationality()
        company_pos = application.getCompanyPos()
        passport_no = application.getPassportNo()
        application_type = application.getApplicationType()
        document_type = application.getDocumentType()
        business_unit = application.getBusinessUnit()
        expiration_date = application.getExpirationDateNoFormat()
        status = application.getStatus()
        deadline = application.getDeadlineNoFormat()
        priority = application.getPriority()
        new_deleted = DeletedApplication(
            firstName = first_name,
            lastName = last_name,
            nationality = nationality,
            companyPos = company_pos,
            passportNo = passport_no,
            applicationType = application_type,
            documentType = document_type,
            businessUnit = business_unit,
            status = status,
            condition = 'Archived',
            expirationDate = expiration_date,
            deadline = deadline,
            priority = priority,
        )
        new_deleted.save()
    Application.objects.filter(pk__in=ids_to_delete).delete()
    return JsonResponse({'status': 'success'}, status=200)

    
        
        

def view_application(request,pk): #add pk here 
    a = get_object_or_404(Application, pk=pk)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        a.status = status
        a.save()
        return redirect('view_dashboard')
    apphist = a.history.all()
    return render(request, 'view_application.html',{'a':a, 'ah':apphist})



from django.contrib.auth import authenticate, login as django_login

def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        raw_password = request.POST.get('password')

        # Authenticate the user using Django's system
        user = authenticate(request, username=email, password=raw_password)
        if user is not None:
            # User is authenticated, proceed to log them in
            django_login(request, user)
            return redirect('view_dashboard')
        else:
            # Authentication failed, handle login error
            messages.error(request, 'Invalid email or password')

    return render(request, 'login.html')

def create_account(request):
    if request.method == "POST":
        admin_pass = request.POST.get('adminpass')
        email = request.POST.get('email')
        username = email
        password = request.POST.get('password')
        confirm_pass = request.POST.get('Cpassword')
        reg = "(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,}$"
        pat = re.compile(reg)
        mat = re.search(pat, password)
        
        if not mat:
            messages.error(request, 'Invalid Password')
            return redirect('create_account')
        if password != confirm_pass:
            messages.error(request, 'Passwords do not match.')
            return redirect('create_account')
        
        if Account.objects.filter(email=email).exists():
            messages.error(request, 'Email address is already registered. Please input a different email address.')
            return redirect('create_account')

        # Placeholder for admin password validation
        if admin_pass != "admin_pass":  # Replace "admin_pass" with the actual admin password
            messages.error(request, 'Admin password provided is incorrect.')
            return redirect('create_account')
        
        # Assuming admin_pass check passes and other validations are ok
        try:
            # Create a User instance
            user = User.objects.create_user(username=username, email=email, password=password)

            # Now you can create the Account instance with a reference to the User instance
            new_account = Account(user=user, username=username, email=email, password=make_password(password))
            new_account.save()
            messages.info(request, 'Account created successfully. You may now log in to the system.')
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

        password_check = request.user.check_password(current_password)

        user = request.user
        account = Account.objects.get(user=user)

        # Update email if it has changed
        if new_email and new_email != request.user.email:
            request.user.email = new_email
            account.email = new_email
            request.user.save()
            account.save()
            messages.error(request, "Your email has been updated.")

        # Change password
        if current_password and new_password and confirm_password:
            print("Current password (from form):", password_check)
            print("Hashed password (from database):", request.user.password)
            if request.user.check_password(current_password):
                if new_password == confirm_password:
                    request.user.password = make_password(new_password)
                    request.user.save()
                    account.password = request.user.check_password(new_password)
                    account.save()
                    # Keep the user logged in after changing the password
                    update_session_auth_hash(request, request.user)
                    messages.success(request, "Your password has been updated.")
                else:
                    messages.error(request, "New passwords do not match.")
            else:
                messages.error(request, "Current password is incorrect.")

        return redirect('edit_account')

    # Pass the user's email to the template to display it
    context = {'user_email': request.user.email, 'user_pass': request.user.password}
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
    additionalinfo = request.POST.get('additional info')
    application.status = status
    currentcomment = application.getComment()
    application.comment = currentcomment + " " + additionalinfo
    application.save()
    
    appstatus = application.getStatus()
    
    if appstatus in ['Approved', 'Rejected', 'Expired']:
        first_name = application.getFirstName()
        last_name = application.getLastName()
        nationality = application.getNationality()
        company_pos = application.getCompanyPos()
        passport_no = application.getPassportNo()
        application_type = application.getApplicationType()
        document_type = application.getDocumentType()
        business_unit = application.getBusinessUnit()
        expiration_date = application.getExpirationDateNoFormat()
        deadline = application.getDeadlineNoFormat()
        priority = application.getPriority()
        new_archived = ApplicationArchive(
            firstName = first_name,
            lastName = last_name,
            nationality = nationality,
            companyPos = company_pos,
            passportNo = passport_no,
            applicationType = application_type,
            documentType = document_type,
            businessUnit = business_unit,
            status = appstatus,
            condition = 'Archived',
            expirationDate = expiration_date,
            deadline = deadline,
            priority = priority,
        )
        new_archived.save()
        Application.objects.filter(pk=pk).delete()
        
        return redirect('view_dashboard')
    
    return redirect('view_dashboard')

def view_checklist(request):
    checklist_list = Checklist.objects.all()
    paginator = Paginator(checklist_list, 7)  # Show 10 checklists per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'document_type_choices': Checklist.document_types,
        'page_obj': page_obj,
    }

    return render(request, 'checklist.html', context)

def create_checklist(request):
    if request.method == 'POST':
        Checklist.objects.create(name='Untitled Checklist')
        return redirect('view_checklist')
    return render(request, 'checklist.html', {'page_obj': Checklist.objects.all()})

def add_checklist_item(request, checklist_id):
    checklist = get_object_or_404(Checklist, id=checklist_id)
    
    if request.method == 'POST':
        item_name = request.POST.get('item')
        if item_name:
            ChecklistItem.objects.create(checklist=checklist, item=item_name)
    
    return redirect('view_checklist')

def update_checklist(request, checklist_id):
    checklist = get_object_or_404(Checklist, id=checklist_id)

    if request.method == 'POST':
        checklist_name = request.POST.get('checklist_name', '')
        docu_type = request.POST.get('docuType', '')
        country = request.POST.get('country', '')
        new_items_json = request.POST.get('newItemsArray', '[]')
        new_items = json.loads(new_items_json)
        item_values = request.POST.getlist('items[]')
        items_to_delete = request.POST.getlist('delete_items[]')

        print("Checklist Name:", checklist_name)
        print("Document Type:", docu_type)
        print("Country:", country)
        print("Existing Items:", item_values)
        print("Items to Delete:", items_to_delete)
        print("New Items:", new_items)

        # Update checklist name, doc type, and country
        if checklist_name:
            checklist.name = checklist_name
        checklist.document_type = docu_type  # Assuming Checklist model has a `document_type` field
        checklist.country = country  # Assuming Checklist model has a `country` field
        checklist.save()

        # Delete items by their database IDs
        if items_to_delete:
            ChecklistItem.objects.filter(id__in=items_to_delete).delete()

        # Update existing items by their IDs
        for item in checklist.items.all():
            item_id = str(item.id)
            if item_id in item_values:
                item_name = request.POST.get(f'item_{item_id}')
                if item_name:
                    item.item = item_name
                    item.save()

        # Add new items
        for new_item_name in new_items:
            if new_item_name.strip():
                ChecklistItem.objects.create(checklist=checklist, item=new_item_name)

        return redirect('view_checklist')

    return render(request, 'update_checklist.html', {'checklist': checklist})

from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

def email(request):
    for app in Application.objects.filter(priority=3): #if we can't implement real time updating of priority change this to manually get the days left
        subj = render_to_string('email-subject.html', {'app': app})
        cont = render_to_string('email-content.html', {'app': app})
        user = request.user
        acc = Account.objects.filter(user=user)
        useremails = acc.getEmail()

        Email = EmailMessage(
            subj,
            cont,
            settings.EMAIL_HOST_USER,
            useremails,
        )

        Email.send()
