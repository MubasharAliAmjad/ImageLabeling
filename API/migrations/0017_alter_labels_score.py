# Generated by Django 4.2.6 on 2023-11-17 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0016_remove_labels_range_remove_labels_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='labels',
            name='score',
            field=models.CharField(max_length=20),
        ),
    ]
