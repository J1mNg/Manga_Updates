# Generated by Django 2.2.5 on 2020-03-07 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MangaSeries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('last_updated', models.DateTimeField(blank=True, null=True)),
                ('paused', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='MangaChapters',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chapter_name', models.CharField(max_length=100)),
                ('manga_series', models.ForeignKey(on_delete='cascade', related_name='manga_series', to='updates.MangaSeries')),
            ],
        ),
    ]
