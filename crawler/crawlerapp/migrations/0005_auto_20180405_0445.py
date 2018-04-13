# Generated by Django 2.0.3 on 2018-04-05 04:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawlerapp', '0004_job_executed'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='job_id',
            field=models.CharField(default='', max_length=15),
        ),
        migrations.AddField(
            model_name='video',
            name='job_name',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='job',
            name='cc_enabled',
            field=models.CharField(default='', max_length=50),
        ),
    ]