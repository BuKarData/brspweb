# oferty/api.py
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from oferty.models import Oferta
import json
from datetime import datetime, date
import csv
from io import StringIO, BytesIO
from openpyxl import Workbook

class RaportAPIView(View):
    """Endpointy API zwracające raporty w różnych formatach"""
    
    def get_dane_dewelopera(self):
        return {
            "nip": "8261116680",
            "regon": "540649478",
            "nazwa_firmy": "B.Z-BUD Beata Żochowska",
            "wojewodztwo": "MAZOWIECKIE",
            "powiat": "wołomiński",
            "gmina": "Zielonka",
            "miejscowosc": "Zielonka",
            "ulica": "Kilińskiego 92A",
            "kod_pocztowy": "05-220",
            "kraj": "Polska",
            "telefon": "502930015",
            "email": "braspol@onet.pl",
            "strona_www": "https://www.braspol.pl"
        }

    def _build_flattened_records(self, dane_dewelopera, oferty, max_pom, max_rab, max_swi):
        for oferta in oferty:
            ceny_list = list(oferta.ceny.all())
            ostatnia_cena = ceny_list[-1] if ceny_list else None
            cena_m2 = (
                round(float(ostatnia_cena.kwota) / float(oferta.metraz), 2)
                if ostatnia_cena and oferta.metraz else ""
            )

            rekord_csv = {
                "nip": dane_dewelopera["nip"],
                "regon": dane_dewelopera["regon"],
                "nazwa_firmy": dane_dewelopera["nazwa_firmy"],
                "wojewodztwo": dane_dewelopera.get("wojewodztwo", ""),
                "powiat": dane_dewelopera.get("powiat", ""),
                "gmina": dane_dewelopera.get("gmina", ""),
                "miejscowosc": dane_dewelopera.get("miejscowosc", ""),
                "ulica": dane_dewelopera.get("ulica", ""),
                "kod_pocztowy": dane_dewelopera.get("kod_pocztowy", ""),
                "kraj": dane_dewelopera.get("kraj", ""),
                "telefon": dane_dewelopera.get("telefon", ""),
                "email": dane_dewelopera.get("email", ""),
                "strona_www": dane_dewelopera.get("strona_www", ""),
                "id_oferty": oferta.id,
                "numer_lokalu": oferta.numer_lokalu,
                "numer_oferty": oferta.numer_oferty if hasattr(oferta, 'numer_oferty') else "",
                "rodzaj_lokalu": oferta.rodzaj_lokalu.nazwa if oferta.rodzaj_lokalu else "",
                "metraz": float(oferta.metraz) if oferta.metraz else "",
                "pokoje": oferta.pokoje,
                "status": oferta.status,
                "cena_pln": float(ostatnia_cena.kwota) if ostatnia_cena else "",
                "cena_za_m2_pln": cena_m2,
                "data_ceny": ostatnia_cena.data.isoformat() if ostatnia_cena else "",
                "inwestycja_nazwa": oferta.inwestycja.nazwa if oferta.inwestycja else "",
                "inwestycja_adres": oferta.inwestycja.adres if oferta.inwestycja else "",
                "inwestycja_id": oferta.inwestycja.id if oferta.inwestycja else "",
            }

            for i, p in enumerate(oferta.pomieszczenia_przynalezne.all()):
                rekord_csv[f"pomieszczenie_{i+1}"] = p.nazwa
            for i, r in enumerate(oferta.rabaty.all()):
                rekord_csv[f"rabat_{i+1}"] = r.nazwa
            for i, s in enumerate(oferta.inne_swiadczenia.all()):
                rekord_csv[f"swiadczenie_{i+1}"] = s.nazwa

            yield rekord_csv

    def get_jsonld_data(self):
        """Generuje dane w formacie JSON-LD"""
        dane_dewelopera = self.get_dane_dewelopera()
        oferty = Oferta.objects.prefetch_related(
            "ceny", "inwestycja", "pomieszczenia_przynalezne", "rabaty", "inne_swiadczenia"
        ).all()

        raport_data = {
            "@context": "https://schema.org/",
            "@type": "Dataset",
            "name": "Raport ofert deweloperskich",
            "description": "Aktualne oferty mieszkań firmy B.Z-BUD Beata Żochowska",
            "dateModified": datetime.now().date().isoformat(),
            "creator": {
                "@type": "Organization",
                "name": dane_dewelopera["nazwa_firmy"],
                "vatID": dane_dewelopera["nip"],
                "taxID": dane_dewelopera["regon"]
            },
            "offers": []
        }

        for oferta in oferty:
            ceny_list = list(oferta.ceny.all())
            ostatnia_cena = ceny_list[-1] if ceny_list else None
            cena_m2 = (
                round(float(ostatnia_cena.kwota) / float(oferta.metraz), 2)
                if ostatnia_cena and oferta.metraz else None
            )

            offer_data = {
                "@type": "Offer",
                "itemOffered": {
                    "@type": "Apartment",
                    "name": f"Mieszkanie {oferta.numer_lokalu}",
                    "floorSize": {
                        "@type": "QuantitativeValue",
                        "value": float(oferta.metraz) if oferta.metraz else None,
                        "unitCode": "m2"
                    },
                    "numberOfRooms": oferta.pokoje
                },
                "price": float(ostatnia_cena.kwota) if ostatnia_cena else None,
                "priceCurrency": "PLN",
                "validFrom": ostatnia_cena.data.isoformat() if ostatnia_cena else None,
                "pricePerM2": cena_m2
            }
            raport_data["offers"].append(offer_data)

        return raport_data

    def get_csv_data(self):
        """Generuje dane w formacie CSV"""
        dane_dewelopera = self.get_dane_dewelopera()
        oferty = Oferta.objects.prefetch_related(
            "ceny", "inwestycja", "pomieszczenia_przynalezne", "rabaty", "inne_swiadczenia"
        ).all()

        max_pom = max((oferta.pomieszczenia_przynalezne.count() for oferta in oferty), default=0)
        max_rab = max((oferta.rabaty.count() for oferta in oferty), default=0)
        max_swi = max((oferta.inne_swiadczenia.count() for oferta in oferty), default=0)

        fieldnames = [
            "nip", "regon", "nazwa_firmy",
            "wojewodztwo", "powiat", "gmina", "miejscowosc", "ulica", "kod_pocztowy", "kraj",
            "telefon", "email", "strona_www",
            "id_oferty", "numer_lokalu", "numer_oferty", "rodzaj_lokalu",
            "metraz", "pokoje", "status", "cena_pln", "cena_za_m2_pln", "data_ceny",
            "inwestycja_nazwa", "inwestycja_adres", "inwestycja_id",
        ]
        fieldnames += [f"pomieszczenie_{i+1}" for i in range(max_pom)]
        fieldnames += [f"rabat_{i+1}" for i in range(max_rab)]
        fieldnames += [f"swiadczenie_{i+1}" for i in range(max_swi)]

        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()

        for rekord_csv in self._build_flattened_records(dane_dewelopera, oferty, max_pom, max_rab, max_swi):
            writer.writerow(rekord_csv)

        return output.getvalue()

    def get_xlsx_data(self):
        """Generuje dane w formacie XLSX"""
        dane_dewelopera = self.get_dane_dewelopera()
        oferty = Oferta.objects.prefetch_related(
            "ceny", "inwestycja", "pomieszczenia_przynalezne", "rabaty", "inne_swiadczenia"
        ).all()

        max_pom = max((oferta.pomieszczenia_przynalezne.count() for oferta in oferty), default=0)
        max_rab = max((oferta.rabaty.count() for oferta in oferty), default=0)
        max_swi = max((oferta.inne_swiadczenia.count() for oferta in oferty), default=0)

        fieldnames = [
            "nip", "regon", "nazwa_firmy",
            "wojewodztwo", "powiat", "gmina", "miejscowosc", "ulica", "kod_pocztowy", "kraj",
            "telefon", "email", "strona_www",
            "id_oferty", "numer_lokalu", "numer_oferty", "rodzaj_lokalu",
            "metraz", "pokoje", "status", "cena_pln", "cena_za_m2_pln", "data_ceny",
            "inwestycja_nazwa", "inwestycja_adres", "inwestycja_id",
        ]
        fieldnames += [f"pomieszczenie_{i+1}" for i in range(max_pom)]
        fieldnames += [f"rabat_{i+1}" for i in range(max_rab)]
        fieldnames += [f"swiadczenie_{i+1}" for i in range(max_swi)]

        wb = Workbook()
        ws = wb.active
        ws.title = "Raport ofert"
        ws.append(fieldnames)

        for rekord in self._build_flattened_records(dane_dewelopera, oferty, max_pom, max_rab, max_swi):
            row = [rekord.get(field, "") for field in fieldnames]
            ws.append(row)

        output = BytesIO()
        wb.save(output)
        return output.getvalue()

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        format_type = kwargs.get('format')
        
        if format_type == 'jsonld':
            data = self.get_jsonld_data()
            response = JsonResponse(data, json_dumps_params={'ensure_ascii': False})
            response['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
            response['Content-Disposition'] = 'inline; filename="raport_ofert.jsonld"'
            return response
            
        elif format_type == 'csv':
            data = self.get_csv_data()
            response = HttpResponse(data, content_type='text/csv; charset=utf-8-sig')
            response['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
            response['Content-Disposition'] = 'inline; filename="raport_ofert.csv"'
            return response
            
        elif format_type == 'xlsx':
            data = self.get_xlsx_data()
            response = HttpResponse(data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
            response['Content-Disposition'] = 'inline; filename="raport_ofert.xlsx"'
            return response
            
        else:
            return JsonResponse({'error': 'Nieobsługiwany format'}, status=400)