# Generated by Django 4.2.6 on 2023-11-17 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0018_alter_labels_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='slice',
            field=models.ManyToManyField(to='API.slice'),
        ),
        migrations.AddField(
            model_name='slice',
            name='score',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='slice',
            name='session_name',
            field=models.CharField(default='string', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='slice',
            name='case_name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='slice',
            name='category_type_name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='slice',
            name='image_id',
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='slice',
            name='labels',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='slice',
            name='options',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
