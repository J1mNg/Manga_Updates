# Generated by Django 2.2.5 on 2020-03-24 09:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('updates', '0006_auto_20200324_2033'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mangaseries',
            name='image',
        ),
    ]
