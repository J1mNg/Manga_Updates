# Generated by Django 2.2.5 on 2020-03-08 05:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('updates', '0002_auto_20200308_1637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mangachapters',
            name='manga_series',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='manga_series', to='updates.MangaSeries'),
        ),
    ]