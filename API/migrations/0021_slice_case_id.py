# Generated by Django 4.2.6 on 2023-11-21 04:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0020_alter_session_slice'),
    ]

    operations = [
        migrations.AddField(
            model_name='slice',
            name='case_id',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
