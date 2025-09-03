from django.contrib import admin
from django.urls import path
from oferty import views
from django.conf import settings
from django.conf.urls.static import static
from .api_views import InwestycjaListAPIView, OfertaListAPIView, CenaListAPIView, APISchemaView
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.renderers import JSONOpenAPIRenderer


class SpectacularInlineAPIView(SpectacularAPIView):
    renderer_classes=[JSONOpenAPIRenderer]

    def get(self,request, *args, **kwargs):
        response = super().get(request,*args,**kwargs)
        response['Content-Disposition'] = 'inline' 
        return response



urlpatterns = [
    path('', views.home, name='home'),
    path('oferty/', views.lista_ofert, name='lista_ofert'),
    path('api/inwestycje/', InwestycjaListAPIView.as_view(), name='api-inwestycje'),
    path('api/oferty/', OfertaListAPIView.as_view(), name='api-oferty'),
    path('api/ceny/', CenaListAPIView.as_view(), name='api-ceny'),
    path('api/schema/', SpectacularInlineAPIView.as_view(), name='api-schema')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
