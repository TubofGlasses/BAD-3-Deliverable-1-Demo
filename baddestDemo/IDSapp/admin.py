from django.contrib import admin
from .models import Application, Account, Checklist, ChecklistItem, ApplicationArchive, DeletedApplication

admin.site.register(Application)
admin.site.register(Account)
admin.site.register(Checklist)
admin.site.register(ChecklistItem)
admin.site.register(ApplicationArchive)
admin.site.register(DeletedApplication)
