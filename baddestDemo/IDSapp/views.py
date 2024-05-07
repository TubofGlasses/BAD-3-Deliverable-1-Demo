from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Application, ApplicationArchive, DeletedApplication, Account, Checklist, ChecklistItem
from django.core.paginator import Paginator
from datetime import datetime, timedelta, date
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
import json
import re
import requests
from django.contrib.auth import login as django_login, update_session_auth_hash, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.cache import cache

def fetch_country_name_mapping():
    cached_data = cache.get('country_name_map')
    if cached_data:
        return cached_data

    url = 'https://restcountries.com/v3.1/all'
    response = requests.get(url)
    country_data = response.json()
    code_to_name = {country['cca2']: country['name']['common'] for country in country_data}
    cache.set('country_name_map', code_to_name, timeout=86400)  # Cache for a day
    return code_to_name

def view_dashboard(request):
    # Count applications by their status
    total_applications = Application.objects.count()
    in_progress_count = Application.objects.filter(status='In Progress').count()
    lodged_count = Application.objects.filter(status='Lodged').count()

    application_list = Application.objects.all().order_by('-priority', 'deadline')
    country_name_map = fetch_country_name_mapping()

    today = date.today()
    for application in application_list:
        application.country_name = country_name_map.get(application.nationality, application.nationality)
        
        if application.deadline:
            days_until_deadline = (application.deadline - today).days
            
            # Add blank statements based on the deadline conditions
            if days_until_deadline < 7:
                print("Urgent Email Sent")
            elif days_until_deadline < 30:
                print("Notification Email Sent")

    
    # Map country code to country name
    for application in application_list:
        application.country_name = country_name_map.get(application.nationality, application.nationality)

    paginator = Paginator(application_list, 10)  # Show 10 applications per page
    page_number = request.GET.get('page')
    applications = paginator.get_page(page_number)
    
    context = {
        'applications': applications,
        'total_applications': total_applications,
        'in_progress_count': in_progress_count,
        'lodged_count': lodged_count,
        'selected_filter': '0',  # Default filter
    }

    return render(request, 'dashboard.html', context)

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
            expiration_date_str = request.POST.get('expirationDate')
            try:
                expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d').date()
                today = datetime.today().date()
                next_week = today + timedelta(weeks=1)
                
                if expiration_date <= today or expiration_date < next_week:
                    raise ValueError("Expiration date must be at least one week from today.")
            except (ValueError, TypeError):
                messages.error(request, 'Invalid expiration date. Please select a valid date.')
                return redirect('create_application')

        name_pattern = r"^[a-zA-Z\\p{L}\s\.\-\']+$"

        error_messages = []

        # Check for special characters in first name and last name
        if not re.match(name_pattern, first_name) or not re.match(name_pattern, last_name):
            error_messages.append("Special characters are not allowed.")

        # Check if the application already exists
        if Application.objects.filter(passportNo=passport_no, documentType=document_type).exists():
            error_messages.append("Application already exists.")

        # If there are any errors, display them and redirect
        if error_messages:
            for error in error_messages:
                messages.error(request, error)
            return redirect('create_application')
        
        checklist = None
        if document_type in ['Visa', 'Work Permit']:
            checklist = Checklist.objects.filter(documentType=document_type).first()
            print(f"Assigned checklist for {document_type}: {checklist}")
        elif document_type == 'Passport':
            checklist = Checklist.objects.filter(documentType='Passport', country=nationality).first()
            print(f"Assigned passport checklist for {nationality}: {checklist}")

        # Log error if checklist is not found
        if checklist is None:
            print(f"No checklist found for document type: {document_type}, nationality: {nationality}")


        # Your logic for successful creation goes here
        messages.success(request, 'Application successfully created. The application has been added into the system.')
        
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
            checklist = checklist,
        )

        new_application.save()

        if new_application.getPriority() == 3:
            subj = render_to_string('email-subject.html', {'app': new_application})
            cont = render_to_string('email-content.html', {'app': new_application})
            acc = Account.objects.all().values('email')
            useremails = list(acc)

            Email = EmailMessage(
                subj,
                cont,
                settings.EMAIL_HOST_USER,
                useremails,
            )

            Email.send()

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
            expiration_date_str = request.POST.get('expirationDate')
            try:
                expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d').date()
                today = datetime.today().date()
                next_week = today + timedelta(weeks=1)
                
                if expiration_date <= today or expiration_date < next_week:
                    raise ValueError("Expiration date must be at least one week from today.")
            except (ValueError, TypeError):
                messages.error(request, 'Invalid expiration date. Please select a valid date.')
                return redirect('create_application')

        name_pattern = r"^[a-zA-Z\\p{L}\s\.\-\']+$"

        error_messages = []

        # Check for special characters in first name and last name
        if not re.match(name_pattern, first_name) or not re.match(name_pattern, last_name):
            error_messages.append("Special characters are not allowed.")

        # Check if the application already exists
        if Application.objects.filter(passportNo=passport_no, documentType=document_type).exists():
            error_messages.append("Application already exists.")

        # If there are any errors, display them and redirect
        if error_messages:
            for error in error_messages:
                messages.error(request, error)
            return redirect('create_application')
        
        checklist = None
        if document_type in ['Visa', 'Work Permit']:
            checklist = Checklist.objects.filter(documentType=document_type).first()
            print(f"Assigned checklist for {document_type}: {checklist}")
        elif document_type == 'Passport':
            checklist = Checklist.objects.filter(documentType='Passport', country=nationality).first()
            print(f"Assigned passport checklist for {nationality}: {checklist}")

        # Log error if checklist is not found
        if checklist is None:
            print(f"No checklist found for document type: {document_type}, nationality: {nationality}")


        # Your logic for successful creation goes here
        messages.success(request, 'Application successfully created. The application has been added into the system.')
        
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
            checklist = checklist,
        )

        new_application.save()

        if new_application.getPriority() == 3:
            subj = render_to_string('email-subject.html', {'app': new_application})
            cont = render_to_string('email-content.html', {'app': new_application})
            acc = Account.objects.all().values('email')
            useremails = list(acc)

            Email = EmailMessage(
                subj,
                cont,
                settings.EMAIL_HOST_USER,
                useremails,
            )

            Email.send()

        return redirect('create_application')
    
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
        

def view_application(request, pk):
    a = get_object_or_404(Application, pk=pk)
    checklist = Checklist.objects.filter(documentType=a.documentType, country=a.nationality).first()
    checklists = Checklist.objects.all()
    
    if checklist:
        checklist_items = ChecklistItem.objects.filter(checklist=checklist)
    else:
        checklist_items = []

    # Fetch the country code to name mapping
    code_to_name = fetch_country_name_mapping()
    a.nationality = code_to_name.get(a.nationality, a.nationality)

    if request.method == 'POST':
        status = request.POST.get('status')
        if not status:  # Ensure status is not empty
            status = 'In Progress'  # Assign a default value
        
        a.status = status
        
        additionalinfo = request.POST.get('additional info')
        a.comment = additionalinfo

        checklist_id = request.POST.get('checklist')
        if checklist_id:
            a.checklist_id = checklist_id

        try:
            a.save()
        except IntegrityError as e:
            messages.error(request, f"Error updating application: {str(e)}")
            return redirect('view_application', pk=a.pk)

        if status in ['Approved', 'Rejected', 'Expired']:
            archived_app = ApplicationArchive(
                firstName=a.firstName,
                lastName=a.lastName,
                nationality=a.nationality,
                companyPos=a.companyPos,
                passportNo=a.passportNo,
                applicationType=a.applicationType,
                documentType=a.documentType,
                businessUnit=a.businessUnit,
                status=a.status,
                condition='Archived',
                comment=a.comment,
                expirationDate=a.expirationDate,
                deadline=a.deadline,
                priority=a.priority
            )
            archived_app.save()
            a.delete()

            return redirect('view_dashboard')
        return redirect('view_dashboard')

    apphist = a.history.all()

    return render(request, 'view_application.html', {'a': a, 'ah': apphist, 'checklist': checklist,
                                                     'checklist_items': checklist_items, 'checklists': checklists})

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

        error_messages = []
        
        if not mat:
            error_messages.append('Invalid Password')

        if password != confirm_pass:
            error_messages.append('Passwords do not match.')
        
        if Account.objects.filter(email=email).exists():
            error_messages.append('Email address is already registered. Please input a different email address.')

        # Placeholder for admin password validation
        if admin_pass != "admin_pass":  # Replace "admin_pass" with the actual admin password
            error_messages.append('Admin password provided is incorrect.')

        if error_messages:
            for error in error_messages:
                messages.error(request, error)
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
        user = new_email

        user = request.user
        account = Account.objects.get(user=user)

        # Update email if it has changed
        if new_email and new_email != request.user.email:
            if User.objects.filter(email=new_email).exists():
                messages.error(request, "This email is already in use by another account.")
            else:
                request.user.email = new_email
                account.email = new_email
                request.user.username = new_email  # Assuming the username is based on the email
                account.username = new_email
                request.user.save()
                account.save()
                messages.success(request, "Your email has been updated.")
        else:
            messages.error(request, "Cannot use currently used email.")

        # Change password
        if current_password and new_password and confirm_password:
            reg = "(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,}$"
            pat = re.compile(reg)
            mat = re.search(pat, new_password)

            if request.user.check_password(current_password):
                if new_password == confirm_password:
                    reg = "(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,}$"
                    pat = re.compile(reg)
                    mat = re.search(pat, new_password)
                    if mat:
                        request.user.password = make_password(new_password)
                        request.user.save()
                        account.password = request.user.check_password(new_password)
                        account.save()
                        # Keep the user logged in after changing the password
                        update_session_auth_hash(request, request.user)
                        messages.success(request, "Password changed successfully. Your password has been updated.")
                    else:
                        messages.error(request, 'Invalid Password')
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
    


def view_checklist(request):
    checklist_list = Checklist.objects.all()
    paginator = Paginator(checklist_list, 7)  # Show 7 checklists per page
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
        messages.success(request, 'Checklist created successfully. The checklist has been added into the system.')
        return redirect('view_checklist')
    return render(request, 'checklist.html', {'page_obj': Checklist.objects.all()})

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

        # Check for unique checklist name (excluding "Untitled Checklist")
        if checklist_name and checklist_name != "Untitled Checklist":
            existing_checklist_name = Checklist.objects.filter(name=checklist_name).exclude(id=checklist_id).first()
            if existing_checklist_name:
                messages.error(request, 'Checklist already exists.')
                return redirect('view_checklist')

        # Check for duplicate doc type and country combination
        if docu_type and country:
            existing_checklist_combination = Checklist.objects.filter(documentType=docu_type, country=country).exclude(id=checklist_id).first()
            if existing_checklist_combination:
                messages.error(request, 'Checklist already exists.')
                return redirect('view_checklist')

        print("Checklist Name:", checklist_name)
        print("Document Type:", docu_type)
        print("Country:", country)
        print("Existing Items:", item_values)
        print("Items to Delete:", items_to_delete)
        print("New Items:", new_items)

        existing_items = [item.item for item in checklist.items.exclude(id__in=items_to_delete)]
        duplicate_found = False

        for new_item_name in new_items:
            if new_item_name.strip() and new_item_name in existing_items:
                messages.error(request, f'Item already exists.')
                duplicate_found = True
            elif new_item_name.strip():
                ChecklistItem.objects.create(checklist=checklist, item=new_item_name)
                existing_items.append(new_item_name)

        if duplicate_found:
            return redirect('view_checklist')

        messages.success(request, 'Checklist updated successfully!')

        # Update checklist name, doc type, and country
        if checklist_name:
            checklist.name = checklist_name
        if docu_type:
            checklist.documentType = docu_type 
        if country:
            checklist.country = country 
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

    return render(request, 'view_checklist.html', {'checklist': checklist})

def delete_checklist(request, checklist_id):
    checklist = get_object_or_404(Checklist, id=checklist_id)
    if request.method == 'POST':
        checklist.delete()  # Deletes the checklist and associated items because of cascade delete
        messages.error(request, 'Checklist deleted successfully.')
        return redirect('view_checklist')  # Adjust the redirect to your checklist view

from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

def email(request):
    for app in Application.objects.filter(priority=3): 
        subj = render_to_string('email-subject.html', {'app': app})
        cont = render_to_string('email-content.html', {'app': app})
        acc = Account.objects.all().values('email')
        useremails = list(acc)

        Email = EmailMessage(
            subj,
            cont,
            settings.EMAIL_HOST_USER,
            useremails,
        )

        Email.send()

def filter(request, value):
    if value == '0':
        application_list = Application.objects.all().order_by('-priority', 'deadline')
    elif value == '1':
        application_list = Application.objects.filter(status='In Progress').order_by('-priority', 'deadline')
    elif value == '2':
        application_list = Application.objects.filter(status='Lodged').order_by('-priority', 'deadline')
    else:
        return redirect('view_dashboard')  # Default case, if an unsupported filter value is passed

    country_name_map = fetch_country_name_mapping()
    for application in application_list:
        application.country_name = country_name_map.get(application.nationality, application.nationality)

    paginator = Paginator(application_list, 10)
    page_number = request.GET.get('page')
    applications = paginator.get_page(page_number)

    # Calculate counts for all statuses
    total_all = Application.objects.count()
    total_in_progress = Application.objects.filter(status='In Progress').count()
    total_lodged = Application.objects.filter(status='Lodged').count()

    return render(request, 'dashboard.html', {
        'applications': applications,
        'selected_filter': value,
        'total_applications': total_all,
        'in_progress_count': total_in_progress,
        'lodged_count': total_lodged
    })

from django.db.models import Q

def search(request):
    if request.method == 'POST':
        search = request.POST.get('searchInput')
        application_list = Application.objects.filter(Q(firstName__contains = search) | Q(lastName__contains = search)).order_by('-priority', 'deadline' )
        country_name_map = fetch_country_name_mapping()

        # Map country code to country name
        for application in application_list:
            application.country_name = country_name_map.get(application.nationality, application.nationality)
        
        paginator = Paginator(application_list, 10)  # Show 10 applications per page
        page_number = request.GET.get('page')
        applications = paginator.get_page(page_number)
        
        return render(request, 'dashboard.html', {'applications': applications})  
    return redirect('view_dashboard')