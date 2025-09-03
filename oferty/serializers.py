from rest_framework import serializers
from .models import Oferta, Cena, Inwestycja

class CenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cena
        fields = ["id", "kwota", "data"]

class OfertaSerializer(serializers.ModelSerializer):
    ceny = CenaSerializer(many=True, read_only=True)

    class Meta:
        model = Oferta
        fields = ["id", "nazwa", "metraz", "data_dodania", "ceny"]

class InwestycjaSerializer(serializers.ModelSerializer):
    oferty = OfertaSerializer(many=True, read_only=True)

    class Meta:
        model = Inwestycja
        fields = ["id", "nazwa", "adres", "data_dodania", "oferty"]
