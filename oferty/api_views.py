from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Oferta, Cena
from django.db.models import Prefetch
from .serializers import OfertaSerializer
from rest_framework.generics import ListAPIView


class OfertyAPIView(ListAPIView):
    queryset = Oferta.objects.all().prefetch_related("ceny")
    serializer_class = OfertaSerializer

class OfertyAPIView(APIView):
    """
    API zwracające listę ofert w formacie JSON gotowym dla gov.dane.pl
    """
    def get(self, request):
        ceny_prefetch = Prefetch('ceny', queryset=Cena.objects.order_by('data'))
        oferty = Oferta.objects.prefetch_related(
            'inwestycja', 'pomieszczenia_przynalezne', 'rabaty', 'inne_swiadczenia', ceny_prefetch
        ).all()

        dane_dewelopera = {
            "nip": "8261116680",
            "regon": "540649478",
            "nazwa_firmy": "B.Z-BUD Beata Żochowska",
            "adres_biura": "Zielonka, ul. Ignacego Paderewskiego 61"
        }

        wynik = []

        for oferta in oferty:
            ceny_list = list(oferta.ceny.all())
            ostatnia_cena = ceny_list[-1] if ceny_list else None
            cena_m2 = round(float(ostatnia_cena.kwota)/float(oferta.metraz), 2) if ostatnia_cena and oferta.metraz else None

            rekord = {
                "deweloper": dane_dewelopera,
                "inwestycja": {
                    "unikalny_identyfikator": getattr(oferta.inwestycja, 'unikalny_identyfikator_przedsiewziecia', None),
                    "adres": getattr(oferta.inwestycja, 'adres', None),
                    "numer_pozwolenia_na_budowe": getattr(oferta.inwestycja, 'numer_pozwolenia', None)
                },
                "oferta": {
                    "id": oferta.id,
                    "numer_lokalu": oferta.numer_lokalu,
                    "rodzaj_lokalu": getattr(oferta.rodzaj_lokalu, 'nazwa', None),
                    "metraz": float(oferta.metraz) if oferta.metraz else None,
                    "pokoje": oferta.pokoje,
                    "status": oferta.status,
                    "cena": float(ostatnia_cena.kwota) if ostatnia_cena else None,
                    "cena_za_m2": cena_m2,
                    "data_ceny": ostatnia_cena.data.isoformat() if ostatnia_cena else None
                },
                "dodatkowe_oplaty": {
                    "pomieszczenia_przynaleznie": [{"nazwa": p.nazwa, "cena": float(p.cena)} for p in oferta.pomieszczenia_przynalezne.all()],
                    "rabaty_i_promocje": [{"nazwa": r.nazwa, "wartosc": float(r.wartosc), "typ": r.typ, "data_od": r.data_od.isoformat(), "data_do": r.data_do.isoformat()} for r in oferta.rabaty.all()],
                    "inne_swiadczenia": [{"nazwa": s.nazwa, "kwota": float(s.kwota)} for s in oferta.inne_swiadczenia.all()]
                }
            }

            wynik.append(rekord)

        return Response(wynik, status=status.HTTP_200_OK)