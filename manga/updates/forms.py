from django import forms
from django.core.exceptions import ValidationError
from .models import MangaSeries

class AddMangaForm(forms.Form):
    manga_URL = forms.URLField()

    # form validation
    def clean(self):
        cleaned_data = super().clean()
        manga_URL = cleaned_data.get("manga_URL")

        #only do this check is manga_url is valid so far
        if manga_URL:
            if "mangakakalot" not in manga_URL and "manganelo" not in manga_URL:
                raise forms.ValidationError(
                    "Website must be from mangakakalot or manganelo."
                )
            if MangaSeries.objects.filter(manga_URL=manga_URL).exists():
                raise ValidationError(
                    'Manga already added.'
                )
