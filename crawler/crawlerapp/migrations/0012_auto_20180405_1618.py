# Generated by Django 2.0.3 on 2018-04-05 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawlerapp', '0011_auto_20180405_1550'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='video_duration',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
