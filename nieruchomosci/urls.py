"""
URL configuration for nieruchomosci project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from oferty import views
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Oferty Braspol",
      default_version='v1',
      description="Raporty ofert dla dane.gov.pl",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   generator_class=None,
   authentication_classes=[],
   openapi_version="3.0.2",
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('oferty.urls')),  
    path("oferty/", include("oferty.urls")),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.yaml', schema_view.without_ui(
        cache_timeout=0,
    ), name='schema-yaml'),
]






if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.shortcuts import redirect

def clean_url(request):
    if request.GET:
        return redirect(request.path)