# Generated by Django 4.2.6 on 2023-11-17 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0014_remove_category_type_score_remove_slice_score_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='labels',
            name='range',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='labels',
            name='value',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
