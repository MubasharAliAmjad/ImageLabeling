# Generated by Django 4.2.6 on 2023-11-27 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0021_slice_case_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='labels',
            name='value',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='options',
            name='value',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='reference_folder',
            name='reference_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
