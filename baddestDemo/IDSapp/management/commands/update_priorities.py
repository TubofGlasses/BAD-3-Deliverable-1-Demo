from django.core.management.base import BaseCommand
from IDSapp.models import Application
from datetime import date

class Command(BaseCommand):
    help = 'Update application priorities based on deadlines'

    def handle(self, *args, **kwargs):
        today = date.today()
        applications = Application.objects.all()

        for application in applications:
            if application.deadline:
                days_until_deadline = (application.deadline - today).days

                if days_until_deadline < 7:
                    priority = 4  # Special priority
                elif days_until_deadline < 30:
                    priority = 3  # High priority
                elif days_until_deadline < 90:
                    priority = 2  # Medium priority
                else:
                    priority = 1  # Low priority
                
                if application.priority != priority:
                    application.priority = priority
                    application.save()

        self.stdout.write(self.style.SUCCESS('Priorities updated successfully!'))