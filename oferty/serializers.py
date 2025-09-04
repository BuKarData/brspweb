from rest_framework import serializers
from .models import Inwestycja, Oferta, Cena, InwestycjaZdjecie, RodzajLokalu, PomieszczeniePrzynalezne, SwiadczeniePieniezne, Rabat

class InwestycjaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inwestycja
        fields = '__all__'

class OfertaSerializer(serializers.ModelSerializer):
    inwestycja = InwestycjaSerializer(read_only=True)
    
    class Meta:
        model = Oferta
        fields = '__all__'

class CenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cena
        fields = '__all__'

class InwestycjaZdjecieSerializer(serializers.ModelSerializer):
    class Meta:
        model = InwestycjaZdjecie
        fields = '__all__'

class RodzajLokaluSerializer(serializers.ModelSerializer):
    class Meta:
        model = RodzajLokalu
        fields = '__all__'

class PomieszczeniePrzynalezneSerializer(serializers.ModelSerializer):
    class Meta:
        model = PomieszczeniePrzynalezne
        fields = '__all__'

class SwiadczeniePieniezneSerializer(serializers.ModelSerializer):
    class Meta:
        model = SwiadczeniePieniezne
        fields = '__all__'

class RabatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rabat
        fields = '__all__'
