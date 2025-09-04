from rest_framework import generics
from .models import Oferta, Inwestycja, Cena
from .serializers import OfertaSerializer, InwestycjaSerializer, CenaSerializer

# Lista ofert
class OfertaListAPIView(generics.ListAPIView):
    queryset = Oferta.objects.all()
    serializer_class = OfertaSerializer

# Lista inwestycji
class InwestycjaListAPIView(generics.ListAPIView):
    queryset = Inwestycja.objects.all()
    serializer_class = InwestycjaSerializer

# Lista cen
class CenaListAPIView(generics.ListAPIView):
    queryset = Cena.objects.all()
    serializer_class = CenaSerializer
