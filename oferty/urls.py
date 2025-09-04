from django.contrib import admin
from django.urls import path, include
from oferty import views
from django.conf import settings
from django.conf.urls.static import static
from .api import DataAPIView 

urlpatterns = [
    path('', views.home, name='home'),
    path('oferty/', views.lista_ofert, name='lista_ofert'),
    path('api/data.jsonld', DataAPIView.as_view(), name='data-jsonld'),
    path('api/data.csv', DataAPIView.as_view(), name='data-csv'),
    path('api/data.xlsx', DataAPIView.as_view(), name='data-xlsx'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)