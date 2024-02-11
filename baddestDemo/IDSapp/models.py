from django.db import models

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
    expirationDate = models.DateField()
    deadline
    status = models.CharField(max_length = 20, selection = statuses)
    applicationType = models.CharField(max_length = 20, selection = application_types)
    documentType = models.CharField(max_length = 20, selection = document_types)
    businessUnit = models.CharField(max_length = 50)
    condition = models.CharField(max_length = 10, selection = conditions)
    comment = models.TextField(blank=True, null=True)
    priority

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
    
    def getCompanyPos(self):
        return self.companyPos
    
    def getCompanyPos(self):
        return self.companyPos
    
    def getCompanyPos(self):
        return self.companyPos
    
    def getCompanyPos(self):
        return self.companyPos


