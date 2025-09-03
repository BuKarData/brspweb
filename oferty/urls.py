from django.contrib import admin
from django.urls import path, include
from oferty import views
from django.conf import settings
from django.conf.urls.static import static
from .api_views import OfertyAPIView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('', views.home, name='home'),
    path('oferty/', views.lista_ofert, name='lista_ofert'),

    path('api/oferty/', OfertyAPIView.as_view(), name='api_oferty'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
