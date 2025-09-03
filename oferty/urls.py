from django.contrib import admin
from django.urls import path, include
from oferty import views
from django.conf import settings
from django.conf.urls.static import static
from .api_views import OfertyAPIView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.renderers import JSONOpenAPIRenderer
from django.urls import path
from .api_views import InwestycjaListAPIView

urlpatterns = [
    path('', views.home, name='home'),
    path('oferty/', views.lista_ofert, name='lista_ofert'),

    # API
    path("api/inwestycje/", InwestycjaListAPIView.as_view(), name="api-inwestycje"),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-docs"),
]


class SpectacularInlineAPIView(SpectacularAPIView):
    renderer_classes=[JSONOpenAPIRenderer]

    def get(self,request, *args, **kwargs):
        response = super().get(request,*args,**kwargs)
        response['Content-Disposition'] = 'inline' 
        return response


urlpatterns = [
    path('', views.home, name='home'),
    path('oferty/', views.lista_ofert, name='lista_ofert'),
    path('api/oferty/', OfertyAPIView.as_view(), name='api-oferty'),
    path('api/schema/', SpectacularInlineJSONAPIView.as_view(), name='api-schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='api-docs'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
