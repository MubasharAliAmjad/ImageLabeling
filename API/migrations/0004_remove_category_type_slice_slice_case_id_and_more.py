# Generated by Django 4.2.6 on 2023-11-08 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0003_rename_zoom_slice_image_id_remove_image_slice_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category_type',
            name='slice',
        ),
        migrations.AddField(
            model_name='slice',
            name='case_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='slice',
            name='project_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='SliceSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slice', models.ManyToManyField(to='API.slice')),
            ],
        ),
    ]