from django.shortcuts import render
from django.urls import reverse_lazy

from django.views.generic import FormView, ListView, CreateView, DeleteView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.exceptions import ValidationError

from django import forms
from .forms import AddMangaForm
from .models import MangaSeries, MangaChapters

from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv
import webbrowser

from datetime import datetime, timedelta

from celery import shared_task
from celery.task import Task
from celery_progress.backend import ProgressRecorder

#Class to get values from the manga webpage
class MangaURLValues(object):
    #THIS MUST BE CALLED FIRST BEFORE OTHERS --> PRIORITY
    #scrapes website and returns soup (processed HTML)
    #param {val} --> the URL of website
    @staticmethod
    def get_soup(val):
        try:
            page_response = requests.get(str(val))
            page_content = BeautifulSoup(page_response.content, "html.parser")
            return page_content
        except (ConnectionError):
            print("A")
            ####do some error checking here if URL is invalid

    #This function --> returns the list of all chapters for a manga website URL
    #param {manga_URL} --> the URL of website
    #uses self.get_soup()
    def get_chapterList(self, manga_URL):
        page_content = self.get_soup(manga_URL)
        chapterList = []
        #use beautifulsoup to
        filtered = page_content.findAll(lambda tag: tag.name == 'div' and tag.get('class') == ['row'])[:10]
        #for all div tags in the soup, find the ones with class == 'row' EXACTLY
        #output first 10 chapters
        if not filtered:
            filtered = page_content.findAll(lambda tag: tag.name == 'li' and tag.get('class') == ['a-h'])[:10]
        for div in filtered:
            #under each div tag, find the title of the a tag, which contains the title of the manga
            chapter = div.find('a')['href']
            #Adds a new entry to the list for every chapter
            chapterList.append(chapter)
        self.chapterList = chapterList
        return self.chapterList

    #This function --> returns the name of manga from soup
    #param {manga_URL} --> the URL of website
    #uses self.get_soup()
    def get_mangaName(self, manga_URL):
        page_content = self.get_soup(manga_URL)
        manga_firstTag = page_content.find("ul", { "class" : "manga-info-text" })
        try:
            if manga_firstTag is None:
                self.mangaName = page_content.find("div", { "class" : "story-info-right" }).find('h1').text
            else:
                self.mangaName = manga_firstTag.findNext('h1').text
        except:
            return False
        return self.mangaName

    def get_latestChapter(self, manga_URL):
        page_content = self.get_soup(manga_URL)
        chapter_fullName = page_content.find(lambda tag: tag.name == 'div' and tag.get('class') == ['row'])
        if not chapter_fullName:
            chapter_fullName = page_content.find(lambda tag: tag.name == 'li' and tag.get('class') == ['a-h'])
        self.chapter_name = chapter_fullName.find('a').contents[0]
        return self.chapter_name

# celery progress bar for updating manga backend
class Update(Task):
    name = "myapp.mytask"

    def update_manga(self):
        progress_recorder = ProgressRecorder(self)
        updated = 0
        for manga in MangaSeries.objects.filter(paused=False):
            manga_URL = manga.manga_URL
            manga_chapters = MangaChapters.objects.filter(manga_series=manga)

            # update the last_updated field
            manga.last_updated = datetime.now()
            manga.save()

            old_chapters_list = manga_chapters.values_list('chapter_URL', flat=True)
            updated_chapters_list = MangaURLValues().get_chapterList(manga_URL)

            difference_manga_list = [item for item in updated_chapters_list if item not in old_chapters_list]

            if difference_manga_list:
                # update database with newest CHAPTERS
                updated += 1

                ### what is more efficient? delete all chapters and update??? ORRR delete the difference and update???
                manga_chapters.delete()
                for chapter in updated_chapters_list:
                    manga_latest_data = MangaChapters(chapter_URL=chapter, manga_series=manga)
                    manga_latest_data.save()

                # open the chapters
                for item in difference_manga_list:
                    webbrowser.open(str(item))

            progress_recorder.set_progress(i + 1, seconds)

        return updated


# Create your views here.

# order the objects being displayed --> paused at the bottom --> otherwise name alphabetical
# use template tags to get latest chapter

def homepage(request):
    manga_series = MangaSeries.objects.all()
    return render(request, "index.html", {'manga_series':manga_series})

def add_manga(request):
    if request.method == 'POST':
        # get data from form
        form = AddMangaForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            manga_URL = data['manga_URL']

            # use class to get manga name and list of 10 latest chapters
            website = MangaURLValues()
            website_manga_name = website.get_mangaName(manga_URL)

            ### VALIDATION NEEDED FOR NO CHAPTERS AND URL 404 NOT FOUND
            # error message needs to be red

            if website_manga_name == False:
                messages.add_message(request, messages.INFO, "manga not found.")
                return render(request, "add_manga.html", {"form":form})

            # returns list of 10 latest manga as manga URL
            website_manga_chapters = website.get_chapterList(manga_URL)

            # datetime object for when manga is added
            now = datetime.now()

            # add the manga series to database
            manga_series_data = MangaSeries(name=website_manga_name, manga_URL=manga_URL, last_updated=now)
            manga_series_data.save()

            # add the 10 lateste chapters associated with the manga series
            for chapter in website_manga_chapters:
                manga_latest_data = MangaChapters(chapter_URL=chapter, manga_series=manga_series_data)
                manga_latest_data.save()

            messages.add_message(request, messages.INFO, str(website_manga_name) + " successfully added.")
    else:
        form = AddMangaForm()

    return render(request, "add_manga.html", {"form":form})

def update_manga(request):
    if request.method == 'POST':
        request_button = request.POST
        if 'update_now' in request_button:
            #updated = Update.delay()

            for manga in MangaSeries.objects.filter(paused=False):
                manga_URL = manga.manga_URL
                manga_chapters = MangaChapters.objects.filter(manga_series=manga)

                # update the last_updated field
                manga.last_updated = datetime.now()
                manga.save()

                old_chapters_list = manga_chapters.values_list('chapter_URL', flat=True)
                updated_chapters_list = MangaURLValues().get_chapterList(manga_URL)

                difference_manga_list = [item for item in updated_chapters_list if item not in old_chapters_list]

                if difference_manga_list:
                    # update database with newest CHAPTERS

                    ### what is more efficient? delete all chapters and update??? ORRR delete the difference and update???
                    manga_chapters.delete()
                    for chapter in updated_chapters_list:
                        manga_latest_data = MangaChapters(chapter_URL=chapter, manga_series=manga)
                        manga_latest_data.save()

                    # open the chapters
                    for item in difference_manga_list:
                        webbrowser.open(str(item))

    return render(request, "update_manga.html")
