# Generated by Django 5.0.1 on 2024-05-02 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IDSapp', '0004_checklist_application_middlename_checklistitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='checklist',
            name='country',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='checklist',
            name='documentType',
            field=models.CharField(choices=[('Visa', 'Visa'), ('Passport', 'Passport'), ('Work Permit', 'Work Permit')], max_length=20, null=True),
        ),
    ]
