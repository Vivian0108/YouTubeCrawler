# Generated by Django 2.0.3 on 2018-06-04 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawlerapp', '0025_auto_20180604_1738'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='filtered_videos',
            field=models.TextField(default=''),
        ),
    ]