# oferty/urls_api.py
from django.urls import path
from . import views

urlpatterns = [
    path('raport/', views.raport_jsonl, name='raport_jsonl'),
]
