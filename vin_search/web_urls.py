"""
Web URLs для VIN поиска
"""
from django.urls import path
from . import web_views

app_name = 'vin_search_web'

urlpatterns = [
    path('', web_views.vin_search_home, name='home'),
    path('search/', web_views.vin_search_results, name='search'),
    path('request/<int:request_id>/', web_views.vin_request_detail, name='request_detail'),
    path('my-requests/', web_views.my_requests, name='my_requests'),
]
