# Generated by Django 4.2.6 on 2023-11-08 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0007_remove_slice_case_id_remove_slice_category_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='sliceSession',
            field=models.ManyToManyField(blank=True, to='API.slicesession'),
        ),
    ]
