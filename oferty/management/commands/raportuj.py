from django.core.management.base import BaseCommand
from oferty.models import Oferta
import requests
import json
from datetime import datetime, date
import csv
import os
from openpyxl import Workbook



class Command(BaseCommand):
    help = "Generuje dzienny raport ofert w formatach JSONL/JSON-LD, CSV i XLSX, a następnie wysyła go do API."

    def generate_csv_report(self, dane_dewelopera, oferty):
        raporty_dir = "raporty"
        if not os.path.exists(raporty_dir):
            os.makedirs(raporty_dir)

        data_raportu = str(date.today())
        nazwa_pliku = f"{raporty_dir}/Raport ofert firmy BZ-Bud_{data_raportu}.csv"

        # Maksymalna liczba elementów w listach
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

        with open(nazwa_pliku, "w", newline="", encoding="utf-8-sig") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()

            for rekord_csv in self._build_flattened_records(dane_dewelopera, oferty, max_pom, max_rab, max_swi):
                writer.writerow(rekord_csv)

        self.stdout.write(self.style.SUCCESS(f"Raport CSV został wygenerowany: {nazwa_pliku}"))

    def generate_xlsx_report(self, dane_dewelopera, oferty):
        raporty_dir = "raporty"
        if not os.path.exists(raporty_dir):
            os.makedirs(raporty_dir)

        data_raportu = str(date.today())
        nazwa_pliku = f"{raporty_dir}/Raport ofert firmy BZ-Bud_{data_raportu}.xlsx"

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

        wb.save(nazwa_pliku)
        self.stdout.write(self.style.SUCCESS(f"Raport XLSX został wygenerowany: {nazwa_pliku}"))

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

    def generate_jsonld_report(self, dane_dewelopera, oferty):
        raporty_dir = "raporty"
        if not os.path.exists(raporty_dir):
            os.makedirs(raporty_dir)

        data_raportu = str(date.today())
        nazwa_pliku = f"{raporty_dir}/raport_{data_raportu}.jsonld"

        raport_lines = []

        jsonld_context = {
            "@vocab": "http://schema.org/",
            "nip": "http://purl.org/nace/NACE2/82.6",
            "regon": "http://purl.org/nace/NACE2/54.0",
            "metraz": "http://purl.org/qudt/vocab/area",
            "cena": "http://purl.org/qudt/vocab/currency",
            "data_raportu": "http://purl.org/dc/terms/date",
        }

        for oferta in oferty:
            ceny_list = list(oferta.ceny.all())
            ostatnia_cena = ceny_list[-1] if ceny_list else None
            cena_m2 = (
                round(float(ostatnia_cena.kwota) / float(oferta.metraz), 2)
                if ostatnia_cena and oferta.metraz else None
            )

            pomieszczenia_przynalezne = [{"nazwa": p.nazwa, "cena": float(p.cena)} for p in oferta.pomieszczenia_przynalezne.all()]
            rabaty = [{"nazwa": r.nazwa, "wartosc": float(r.wartosc), "typ": r.typ} for r in oferta.rabaty.all()]
            inne_swiadczenia = [{"nazwa": s.nazwa, "kwota": float(s.kwota)} for s in oferta.inne_swiadczenia.all()]

            rekord_jsonld = {
                "@context": jsonld_context,
                "@type": "Product",
                "name": f"Oferta nr {oferta.numer_oferty}",
                "description": f"Mieszkanie {oferta.pokoje}-pokojowe o metrażu {oferta.metraz} m2.",
                "offers": {
                    "@type": "Offer",
                    "priceCurrency": "PLN",
                    "price": float(ostatnia_cena.kwota) if ostatnia_cena else None,
                    "validFrom": ostatnia_cena.data.isoformat() if ostatnia_cena else None
                },
                "itemOffered": {
                    "@type": "Apartment",
                    "address": {
                        "@type": "PostalAddress",
                        "streetAddress": oferta.inwestycja.adres if oferta.inwestycja else "",
                        "addressLocality": "Zielonka",
                    },
                    "numberOfRooms": oferta.pokoje,
                    "floorSize": {
                        "@type": "QuantitativeValue",
                        "value": float(oferta.metraz) if oferta.metraz else None,
                        "unitCode": "m2"
                    },
                    "status": oferta.status
                },
                "seller": {
                    "@type": "Organization",
                    "name": dane_dewelopera["nazwa_firmy"],
                    "vatID": dane_dewelopera["nip"],
                    "taxID": dane_dewelopera["regon"],
                    "address": {
                        "@type": "PostalAddress",
                        "streetAddress": dane_dewelopera["ulica"],
                        "addressLocality": dane_dewelopera["miejscowosc"],
                        "addressRegion": dane_dewelopera["wojewodztwo"],
                        "postalCode": dane_dewelopera["kod_pocztowy"],
                        "addressCountry": dane_dewelopera["kraj"],
                    },
                    "telephone": dane_dewelopera.get("telefon", ""),
                    "email": dane_dewelopera.get("email", ""),
                    "url": dane_dewelopera.get("strona_www", "")
                },
                "data_raportu": data_raportu,
                "cena_za_m2": cena_m2,
                "pomieszczenia_przynaleznie": pomieszczenia_przynalezne,
                "rabaty": rabaty,
                "inne_swiadczenia": inne_swiadczenia,
            }

            raport_lines.append(json.dumps(rekord_jsonld, ensure_ascii=False))

        payload_jsonld = "\n".join(raport_lines)
        with open(nazwa_pliku, "w", encoding="utf-8") as f:
            f.write(payload_jsonld)

        self.stdout.write(self.style.SUCCESS(f"Raport JSON-LD został wygenerowany: {nazwa_pliku}"))

    

    def handle(self, *args, **kwargs):
        self.stdout.write("Rozpoczynanie generowania raportów...")

        dane_dewelopera = {
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

        oferty = Oferta.objects.prefetch_related(
            "ceny", "inwestycja", "pomieszczenia_przynalezne", "rabaty", "inne_swiadczenia"
        ).all()

        if not oferty.exists():
            self.stdout.write(self.style.WARNING("Nie znaleziono ofert do raportu."))
            return

        self.generate_csv_report(dane_dewelopera, oferty)
        self.generate_xlsx_report(dane_dewelopera, oferty)
        self.generate_jsonld_report(dane_dewelopera, oferty)

        # Wysyłka JSONL do API
        raport_lines = []
        data_raportu = str(date.today())
        for oferta in oferty:
            if not oferta.inwestycja or not oferta.inwestycja.unikalny_identyfikator_przedsiewziecia:
                self.stdout.write(self.style.ERROR(f"Oferta ID {oferta.id} nie ma inwestycji lub ID."))
                continue

            ceny_list = list(oferta.ceny.all())
            ostatnia_cena = ceny_list[-1] if ceny_list else None
            if not ostatnia_cena:
                self.stdout.write(self.style.WARNING(f"Oferta ID {oferta.id} bez ceny. Pomijam."))
                continue

            cena_m2 = (
                round(float(ostatnia_cena.kwota) / float(oferta.metraz), 2)
                if oferta.metraz else None
            )

            rekord_oferty = {
                "deweloper": {
                    "nip": dane_dewelopera["nip"],
                    "regon": dane_dewelopera["regon"],
                    "nazwa_firmy": dane_dewelopera["nazwa_firmy"],
                    "telefon": dane_dewelopera.get("telefon", ""),
                    "email": dane_dewelopera.get("email", ""),
                    "strona_www": dane_dewelopera.get("strona_www", ""),
                    "kraj": dane_dewelopera.get("kraj", "")
                },
                "inwestycja": {
                    "unikalny_identyfikator": oferta.inwestycja.unikalny_identyfikator_przedsiewziecia,
                    "numer_pozwolenia_na_budowe": oferta.inwestycja.numer_pozwolenia,
                    "termin_rozpoczecia": oferta.inwestycja.termin_rozpoczecia.isoformat() if oferta.inwestycja.termin_rozpoczecia else None,
                    "termin_zakonczenia": oferta.inwestycja.termin_zakonczenia.isoformat() if oferta.inwestycja.termin_zakonczenia else None,
                },
                "oferta": {
                    "id": oferta.id,
                    "numer_lokalu": oferta.numer_lokalu,
                    "numer_oferty": oferta.numer_oferty if hasattr(oferta, 'numer_oferty') else None,
                    "rodzaj_lokalu": oferta.rodzaj_lokalu.nazwa if oferta.rodzaj_lokalu else None,
                    "metraz": float(oferta.metraz) if oferta.metraz else None,
                    "pokoje": oferta.pokoje,
                    "status": oferta.status,
                    "cena": float(ostatnia_cena.kwota),
                    "cena_za_m2": cena_m2,
                    "data_ceny": ostatnia_cena.data.isoformat()
                },
                "dodatkowe_oplaty": {
                    "pomieszczenia_przynaleznie": [{"nazwa": p.nazwa, "cena": float(p.cena)} for p in oferta.pomieszczenia_przynalezne.all()],
                    "rabaty_i_promocje": [{"nazwa": r.nazwa, "wartosc": float(r.wartosc), "typ": r.typ, "data_od": r.data_od.isoformat(), "data_do": r.data_do.isoformat()} for r in oferta.rabaty.all()],
                    "inne_swiadczenia": [{"nazwa": s.nazwa, "kwota": float(s.kwota)} for s in oferta.inne_swiadczenia.all()]
                }
            }
            raport_lines.append(json.dumps(rekord_oferty, ensure_ascii=False))

        if raport_lines:
            payload = "\n".join(raport_lines)
            headers = {
                "Content-Type": "application/x-json-stream; charset=utf-8",
                "Last-Modified": datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
            }
            url_api = "https://webhook.site/63ac4048-0ef4-4847-8787-0fff7d401940"
            try:
                response = requests.post(url_api, headers=headers, data=payload.encode('utf-8'))
                response.raise_for_status()
                self.stdout.write(self.style.SUCCESS(f"Raport JSONL wysłany, status: {response.status_code}"))
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"Błąd wysyłki JSONL: {e}"))      
