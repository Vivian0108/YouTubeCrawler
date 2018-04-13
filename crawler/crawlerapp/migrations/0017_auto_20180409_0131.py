# Generated by Django 2.0.3 on 2018-04-09 01:31

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crawlerapp', '0016_auto_20180406_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='youtube_params',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=list, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='youtube_params',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=list, null=True),
        ),
        migrations.AlterField(
            model_name='playlist',
            name='youtube_params',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=list, null=True),
        ),
        migrations.AlterField(
            model_name='video',
            name='youtube_params',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=list, null=True),
        ),
    ]
