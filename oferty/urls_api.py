from django.urls import path
from .views_api import OfertaListAPIView, InwestycjaListAPIView, CenaListAPIView

urlpatterns = [
    path('oferty/', OfertaListAPIView.as_view(), name='oferta-list'),
    path('inwestycje/', InwestycjaListAPIView.as_view(), name='inwestycja-list'),
    path('ceny/', CenaListAPIView.as_view(), name='cena-list'),
]
