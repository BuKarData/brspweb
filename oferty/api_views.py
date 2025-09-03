from rest_framework import generics
from drf_spectacular.views import SpectacularAPIView
from .models import Inwestycja, Oferta, Cena
from .serializers import InwestycjaSerializer, OfertaSerializer, CenaSerializer


# OpenAPI schema endpoint
class APISchemaView(SpectacularAPIView):
    pass

# Widoki API
class InwestycjaListAPIView(generics.ListAPIView):
    queryset = Inwestycja.objects.all()
    serializer_class = InwestycjaSerializer

class OfertaListAPIView(generics.ListAPIView):
    queryset = Oferta.objects.all()
    serializer_class = OfertaSerializer

class CenaListAPIView(generics.ListAPIView):
    queryset = Cena.objects.all()
    serializer_class = CenaSerializer
