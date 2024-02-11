from django.db import models
from datetime import timedelta, date

# Create your models here.
class Application(models.Model):
    application_types = [
        ('RENEWAL', 'Renewal'),
        ('APPLICATION', 'Application')
    ]

    document_types = [
        ('VISA', 'Visa'),
        ('PASSPORT', 'Passport'),
        ('WORK_PERMIT', 'Work Permit')
    ]

    statuses = [
        ('IN_PROGRESS', 'Renewal'),
        ('LODGED', 'Renewal'),
        ('REJECTED', 'Renewal'),
        ('APPROVED', 'Renewal'),
        ('ARCHIVED', 'Renewal')
    ]

    conditions = [
        ('ACTIVE', 'Active'),
        ('ARCHIVED', 'Archived')
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
    condition = models.CharField(max_length = 10, choices = conditions)
    comment = models.TextField(blank=True, null=True)
    priority = models.IntegerField(default=0)

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
    
    def calculate_deadline(self):
        if self.application_types in 'RENEWAL':
            if self.document_types in ['VISA', 'PASSPORT']:
                return self.expirationDate - timedelta(weeks = 12) # 3 months
            elif self.document_types == 'WORK_PERMIT':
                return self.expirationDate - timedelta(weeks = 16) # 4 months
        else:
            today = date.today()
            return today + timedelta(weeks = 4)
        
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

        super(Application, self).save(*args, **kwargs)


