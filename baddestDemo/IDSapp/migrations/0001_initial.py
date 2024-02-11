# Generated by Django 5.0.1 on 2024-02-11 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(max_length=50)),
                ('lastName', models.CharField(max_length=50)),
                ('nationality', models.CharField(max_length=50)),
                ('companyPos', models.CharField(max_length=50)),
                ('passportNo', models.CharField(max_length=15)),
                ('expirationDate', models.DateField(blank=True, null=True)),
                ('deadline', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('IN_PROGRESS', 'Renewal'), ('LODGED', 'Renewal'), ('REJECTED', 'Renewal'), ('APPROVED', 'Renewal'), ('ARCHIVED', 'Renewal')], max_length=20)),
                ('applicationType', models.CharField(choices=[('RENEWAL', 'Renewal'), ('APPLICATION', 'Application')], max_length=20)),
                ('documentType', models.CharField(choices=[('VISA', 'Visa'), ('PASSPORT', 'Passport'), ('WORK_PERMIT', 'Work Permit')], max_length=20)),
                ('businessUnit', models.CharField(max_length=50)),
                ('condition', models.CharField(choices=[('ACTIVE', 'Active'), ('ARCHIVED', 'Archived')], max_length=10)),
                ('comment', models.TextField(blank=True, null=True)),
                ('priority', models.IntegerField(default=0)),
            ],
        ),
    ]
