# Generated by Django 4.2.6 on 2023-11-29 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0022_alter_labels_value_alter_options_value_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='case',
            name='notes',
        ),
        migrations.AddField(
            model_name='project',
            name='notes',
            field=models.TextField(blank=True),
        ),
    ]
