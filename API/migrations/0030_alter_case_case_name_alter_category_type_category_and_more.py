# Generated by Django 4.2.6 on 2023-12-29 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0029_slice_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='case_name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='category_type',
            name='category',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='category_type',
            name='type',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='labels',
            name='value',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='options',
            name='value',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='reference_folder',
            name='reference_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='session_name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='slice',
            name='case_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='slice',
            name='category_type_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='slice',
            name='labels',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='slice',
            name='options',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='slice',
            name='project_name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='slice',
            name='session_name',
            field=models.CharField(max_length=255),
        ),
    ]