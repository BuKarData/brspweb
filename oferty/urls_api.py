# oferty/urls_api.py
from django.urls import path
from . import views_api

urlpatterns = [
    path('raport/', views_api.raport_jsonl, name='raport_jsonl'),
]
