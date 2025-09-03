# oferty/urls_api.py
from django.urls import path
from . import views_api

urlpatterns = [
    path('', views_api.RaportList.as_view(), name='api_raport_list'),
]
