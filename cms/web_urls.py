"""
Web URLs для CMS страниц
"""
from django.urls import path
from . import web_views

app_name = 'cms_web'

urlpatterns = [
    path('', web_views.contacts, name='contacts'),
    path('about/', web_views.about, name='about'),
    path('news/', web_views.news_list, name='news_list'),
    path('news/<int:news_id>/', web_views.news_detail, name='news_detail'),
]
