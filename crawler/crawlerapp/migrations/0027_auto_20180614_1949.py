# Generated by Django 2.0.3 on 2018-06-14 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawlerapp', '0026_job_filtered_videos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='job_id',
        ),
        migrations.AddField(
            model_name='video',
            name='job_ids',
            field=models.TextField(default=''),
        ),
    ]