# Generated by Django 4.2.6 on 2023-12-14 12:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0025_customuser_project_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='user',
        ),
    ]
