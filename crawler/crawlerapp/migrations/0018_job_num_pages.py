# Generated by Django 2.0.3 on 2018-04-09 03:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawlerapp', '0017_auto_20180409_0131'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='num_pages',
            field=models.IntegerField(default=10),
        ),
    ]
