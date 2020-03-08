from django.db import models

# Create your models here.

class MangaSeries(models.Model):
    #picture
    name = models.CharField(max_length=50)
    manga_URL = models.URLField(default=None, unique=True)
    last_updated =  models.DateTimeField(null=True, blank=True)
    paused = models.BooleanField(default=False)

    def __str__(self):
            return self.name

class MangaChapters(models.Model):
    chapter_URL = models.URLField(default=None)
    manga_series = models.ForeignKey(MangaSeries, related_name="manga_series", on_delete=models.CASCADE)

    def __str__(self):
            return self.chapter_URL
