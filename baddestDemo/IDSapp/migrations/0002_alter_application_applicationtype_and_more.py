# Generated by Django 5.0.1 on 2024-03-31 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IDSapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='applicationType',
            field=models.CharField(choices=[('Renewal', 'Renewal'), ('Application', 'Application')], max_length=20),
        ),
        migrations.AlterField(
            model_name='application',
            name='condition',
            field=models.CharField(choices=[('Active', 'Active'), ('Archived', 'Archived')], max_length=20),
        ),
        migrations.AlterField(
            model_name='application',
            name='documentType',
            field=models.CharField(choices=[('Visa', 'Visa'), ('Passport', 'Passport'), ('Work Permit', 'Work Permit')], max_length=20),
        ),
        migrations.AlterField(
            model_name='application',
            name='status',
            field=models.CharField(choices=[('In Progress', 'In Progress'), ('Lodged', 'Lodged'), ('Rejected', 'Rejected'), ('Approved', 'Approved'), ('Archived', 'Archived')], max_length=20),
        ),
    ]
