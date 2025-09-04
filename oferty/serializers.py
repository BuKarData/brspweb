from rest_framework import serializers
from .models import Inwestycja, Oferta, Cena, InwestycjaZdjecie, RodzajLokalu, PomieszczeniePrzynalezne, SwiadczeniePieniezne, Rabat

class CenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cena
        fields = ['id', 'kwota', 'data']

class OfertaSerializer(serializers.ModelSerializer):
    ceny = CenaSerializer(many=True, read_only=True)

    class Meta:
        model = Oferta
        fields = ['id', 'adres', 'metraz', 'pokoje', 'status', 'numer_lokalu', 'numer_oferty', 'rodzaj_lokalu', 'ceny']

class InwestycjaZdjecieSerializer(serializers.ModelSerializer):
    class Meta:
        model = InwestycjaZdjecie
        fields = ['id', 'obraz']

class InwestycjaSerializer(serializers.ModelSerializer):
    oferty = OfertaSerializer(many=True, read_only=True)
    zdjecia = InwestycjaZdjecieSerializer(many=True, read_only=True)

    class Meta:
        model = Inwestycja
        fields = ['id', 'nazwa', 'adres', 'data_dodania', 'zdjecie', 'opis', 'standard', 'numer_pozwolenia',
                  'termin_rozpoczecia', 'termin_zakonczenia', 'oferty', 'zdjecia']

class RodzajLokaluSerializer(serializers.ModelSerializer):
    class Meta:
        model = RodzajLokalu
        fields = ['id', 'nazwa']

class PomieszczeniePrzynalezneSerializer(serializers.ModelSerializer):
    class Meta:
        model = PomieszczeniePrzynalezne
        fields = ['id', 'nazwa', 'powierzchnia', 'cena']

class SwiadczeniePieniezneSerializer(serializers.ModelSerializer):
    class Meta:
        model = SwiadczeniePieniezne
        fields = ['id', 'nazwa', 'kwota', 'opis']

class RabatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rabat
        fields = ['id', 'nazwa', 'wartosc', 'typ', 'data_od', 'data_do']