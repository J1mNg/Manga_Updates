# Generated by Django 2.2.5 on 2020-03-24 11:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('updates', '0008_mangaseries_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mangaseries',
            name='image',
        ),
    ]
