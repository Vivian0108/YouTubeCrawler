# Generated by Django 2.0.3 on 2018-04-05 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawlerapp', '0010_auto_20180405_0508'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='comments',
        ),
        migrations.RemoveField(
            model_name='video',
            name='rating',
        ),
        migrations.AddField(
            model_name='video',
            name='comment_count',
            field=models.CharField(default='', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='video',
            name='dislike_count',
            field=models.CharField(default='', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='video',
            name='like_count',
            field=models.CharField(default='', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='video',
            name='published_date',
            field=models.CharField(default='', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='video',
            name='view_count',
            field=models.CharField(default='', max_length=50, null=True),
        ),
    ]
