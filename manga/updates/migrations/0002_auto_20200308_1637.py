# Generated by Django 2.2.5 on 2020-03-08 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('updates', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mangachapters',
            name='chapter_name',
        ),
        migrations.AddField(
            model_name='mangachapters',
            name='chapter_URL',
            field=models.URLField(default=None),
        ),
        migrations.AddField(
            model_name='mangaseries',
            name='manga_URL',
            field=models.URLField(default=None),
        ),
    ]