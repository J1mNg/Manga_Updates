from django.urls import path
from . import views

app_name='updates'

urlpatterns = [
    path('add_manga/', views.add_manga, name='updates-add_manga'),
    path('update_manga/', views.update_manga, name='updates-update_manga'),
    path('', views.homepage, name='updates-homepage'),
]
