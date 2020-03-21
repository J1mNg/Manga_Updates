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

# Create your views here.
def homepage(request):

    return render(request, "index.html")

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

            manga_series_data = MangaSeries(name=website_manga_name, manga_URL=manga_URL, last_updated=now)
            manga_series_data.save()

            for chapter in website_manga_chapters:
                manga_latest_data = MangaChapters(chapter_URL=chapter, manga_series=manga_series_data)
                manga_latest_data.save()

            messages.add_message(request, messages.INFO, str(website_manga_name) + " successfully added.")
    else:
        form = AddMangaForm()

    return render(request, "add_manga.html", {"form":form})

def update_manga(request):
    if request.method == 'POST'
        request = request.POST
        if 'update_now' in get_request:
            
