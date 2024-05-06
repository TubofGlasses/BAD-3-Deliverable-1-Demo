from django.db import models
from django.conf import settings
from datetime import timedelta, date

# Create your models here.
class BaseApplication(models.Model):
    
    class Meta:
        abstract = True
        
    application_types = [
        ('Renewal', 'Renewal'),
        ('Application', 'Application')
    ]

    document_types = [
        ('Visa', 'Visa'),
        ('Passport', 'Passport'),
        ('Work Permit', 'Work Permit')
    ]

    statuses = [
        ('In Progress', 'In Progress'),
        ('Lodged', 'Lodged'),
        ('Rejected', 'Rejected'),
        ('Approved', 'Approved'),
        ('Archived', 'Archived')
    ]

    conditions = [
        ('Active', 'Active'),
        ('Archived', 'Archived')
    ]

    firstName = models.CharField(max_length = 50)
    lastName = models.CharField(max_length = 50)
    nationality = models.CharField(max_length = 50)
    companyPos = models.CharField(max_length = 50)
    passportNo = models.CharField(max_length = 15)
    expirationDate = models.DateField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    status = models.CharField(max_length = 20, choices = statuses)
    applicationType = models.CharField(max_length = 20, choices = application_types)
    documentType = models.CharField(max_length = 20, choices = document_types)
    businessUnit = models.CharField(max_length = 50)
    condition = models.CharField(max_length = 20, choices = conditions)
    comment = models.TextField(blank=True, null=True)
    priority = models.IntegerField(default=0)
    objects = models.Manager()

    def getFirstName(self):
        return self.firstName
    
    def getLastName(self):
        return self.lastName

    def getNationality(self):
        return self.nationality
    
    def getCompanyPos(self):
        return self.companyPos
    
    def getPassportNo(self):
        return self.passportNo
    
    def getExpirationDate(self):
        return self.expirationDate.strftime('%m/%d/%Y') if self.expirationDate else None
    
    def getDeadline(self):
        return self.deadline.strftime('%m/%d/%Y') if self.deadline else None
    
    def getExpirationDateNoFormat(self):
        return self.expirationDate if self.expirationDate else None
    
    def getDeadlineNoFormat(self):
        return self.deadline if self.deadline else None
    
    def getStatus(self):
        return self.status
    
    def getApplicationType(self):
        return self.applicationType
    
    def getDocumentType(self):
        return self.documentType

    def getBusinessUnit(self):
        return self.businessUnit

    def getCondition(self):
        return self.condition

    def getComment(self):
        return self.comment

    def getPriority(self):
        return self.priority
        
class Application(BaseApplication):
    def calculate_deadline(self):
        if self.applicationType == 'Renewal':
            if self.documentType in ['Visa', 'Passport']:
                return self.expirationDate - timedelta(weeks=12)
            elif self.documentType == 'Work Permit':
                return self.expirationDate - timedelta(weeks=16)
        else:
            today = date.today()
            return today + timedelta(weeks=12)
        
    def calculate_priority(self):
        today = date.today()
        if self.deadline:
            days_until_deadline = (self.deadline - today).days
            if days_until_deadline < 30:
                return 3 # high priority
            elif days_until_deadline < 90:
                return 2 # medium priority
            else:
                return 1 # low priority
        return 0

    def save(self, *args, **kwargs):
        if self.applicationType == 'APPLICATION':
            self.expirationDate = None

        self.deadline = self.calculate_deadline()
        self.priority = self.calculate_priority()

        super(BaseApplication, self).save(*args, **kwargs)
    pass

class ApplicationArchive(BaseApplication):
    pass

class DeletedApplication(BaseApplication):
    pass

class Account(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    username = models.CharField(max_length = 255, null=True)
    password = models.CharField(max_length = 255)
    email = models.EmailField(max_length = 254)
    objects = models.Manager()

    def getUsername(self):
        return self.username
    
    def getPassword(self):
        return self.password
    
    def getEmail(self):
        return self.email
    
class Checklist(models.Model):
    document_types = [
        ('Visa', 'Visa'),
        ('Passport', 'Passport'),
        ('Work Permit', 'Work Permit')
    ]

    name = models.CharField(max_length=255)
    documentType = models.CharField(max_length = 20, choices = document_types, null=True)
    country =  models.CharField(max_length = 50, null=True)

    def getName(self):
        return self.name
    
    def getDocumentType(self):
        return self.documentType
    
    def getCountry(self):
        return self.country

class ChecklistItem(models.Model):
    checklist = models.ForeignKey(Checklist, related_name='items', on_delete=models.CASCADE)
    item = models.CharField(max_length=255)

    def __str__(self):
        return self.item