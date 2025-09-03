from rest_framework import serializers
from .models import (
    Inwestycja, Oferta, Cena,
    PomieszczeniePrzynalezne, SwiadczeniePieniezne, Rabat
)


class CenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cena
        fields = ["id", "kwota", "data"]


class RabatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rabat
        fields = ["id", "nazwa", "wartosc", "typ", "data_od", "data_do"]


class SwiadczeniePieniezneSerializer(serializers.ModelSerializer):
    class Meta:
        model = SwiadczeniePieniezne
        fields = ["id", "nazwa", "kwota", "opis"]


class PomieszczeniePrzynalezneSerializer(serializers.ModelSerializer):
    class Meta:
        model = PomieszczeniePrzynalezne
        fields = ["id", "nazwa", "powierzchnia", "cena"]


class OfertaSerializer(serializers.ModelSerializer):
    ceny = CenaSerializer(many=True, read_only=True)
    rabaty = RabatSerializer(many=True, read_only=True)
    inne_swiadczenia = SwiadczeniePieniezneSerializer(many=True, read_only=True)
    pomieszczenia_przynalezne = PomieszczeniePrzynalezneSerializer(many=True, read_only=True)

    class Meta:
        model = Oferta
        fields = [
            "id",
            "adres",
            "metraz",
            "pokoje",
            "status",
            "data_dodania",
            "numer_lokalu",
            "numer_oferty",
            "rodzaj_lokalu",
            "ceny",
            "rabaty",
            "inne_swiadczenia",
            "pomieszczenia_przynalezne",
        ]


class InwestycjaSerializer(serializers.ModelSerializer):
    oferty = OfertaSerializer(many=True, read_only=True)

    class Meta:
        model = Inwestycja
        fields = [
            "id",
            "nazwa",
            "adres",
            "data_dodania",
            "opis",
            "standard",
            "unikalny_identyfikator_przedsiewziecia",
            "numer_pozwolenia",
            "termin_rozpoczecia",
            "termin_zakonczenia",
            "oferty",
        ]
