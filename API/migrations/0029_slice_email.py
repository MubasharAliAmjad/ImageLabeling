# Generated by Django 4.2.6 on 2023-12-22 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0028_project_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='slice',
            name='email',
            field=models.EmailField(default='admin@gmail.com', max_length=254),
            preserve_default=False,
        ),
    ]