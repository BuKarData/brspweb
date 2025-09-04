from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Prefetch
from .forms import OfertaForm, CenaForm
from .models import Oferta, Cena, Inwestycja
from .raportuj import generuj_i_zapisz_raport_jsonapi



def raport_jsonapi(request):
    url_pliku = generuj_i_zapisz_raport_jsonapi()
    return JsonResponse({"url": url_pliku})


# Strona główna
#def home(request):
 #   ostatnia_oferta = Oferta.objects.order_by('-data_dodania').first()
  #  return render(request, "home.html", {"ostatnia_oferta": ostatnia_oferta})

def home(request):
    ceny_prefetch = Prefetch('ceny', queryset=Cena.objects.order_by('data'))
    
    inwestycje = Inwestycja.objects.prefetch_related(
        Prefetch('oferty', queryset=Oferta.objects.prefetch_related(ceny_prefetch))
    ).order_by('-data_dodania')

    # Przygotowanie danych dla każdej oferty
    for inwestycja in inwestycje:
        for oferta in inwestycja.oferty.all():
            ceny = list(oferta.ceny.all())
            if ceny:
                ostatnia = ceny[-1]
                oferta.ostatnia_cena = ostatnia.kwota
                oferta.cena_m2 = float(oferta.ostatnia_cena) / float(oferta.metraz) if oferta.metraz else None
            else:
                oferta.ostatnia_cena = None
                oferta.cena_m2 = None

    return render(request, "home.html", {"inwestycje": inwestycje})



def lista_ofert(request):
    ceny_prefetch = Prefetch('ceny', queryset=Cena.objects.order_by('data'))
    oferty = Oferta.objects.all().prefetch_related(ceny_prefetch).order_by('-data_dodania')

    for oferta in oferty:
        ceny = list(oferta.ceny.all())
        oferta.ceny_list = []  # lista dla historii cen

        for c in ceny:
            try:
                kwota = float(c.kwota)
                oferta.ceny_list.append({'kwota': kwota, 'data': c.data})
            except (ValueError, TypeError):
                continue

        if oferta.ceny_list:
            ostatnia = oferta.ceny_list[-1]
            oferta.ostatnia_cena = ostatnia
            oferta.cena_m2 = int(ostatnia['kwota'] / float(oferta.metraz)) if oferta.metraz else None
        else:
            oferta.ostatnia_cena = None
            oferta.cena_m2 = None

        oferta.chart_data = {
            "labels": [str(c['data']) for c in oferta.ceny_list],
            "data": [c['kwota'] for c in oferta.ceny_list],
        }
        
    

    return render(request, "oferty/lista_ofert.html", {"oferty": oferty})

def szczegoly_inwestycji(request, pk):
    inwestycja = get_object_or_404(Inwestycja, pk=pk)
    oferty = inwestycja.oferty.all()  # używamy related_name="oferty"
    return render(request, "oferty/szczegoly_inwestycji.html", {
        "inwestycja": inwestycja,
        "oferty": oferty,
    })



# Dodawanie oferty
def dodaj_oferte(request):
    if request.method == "POST":
        form = OfertaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_ofert')
    else:
        form = OfertaForm()
    return render(request, "oferty/dodaj_oferte.html", {"form": form})


# Dodawanie ceny
def dodaj_cene(request, oferta_id):
    oferta = get_object_or_404(Oferta, id=oferta_id)
    if request.method == "POST":
        form = CenaForm(request.POST)
        if form.is_valid():
            cena = form.save(commit=False)
            cena.oferta = oferta
            cena.save()
            return redirect('lista_ofert')
    else:
        form = CenaForm()
    return render(request, "oferty/dodaj_cene.html", {"form": form, "oferta": oferta})


# AJAX dodawanie ceny
@csrf_exempt
def ajax_dodaj_cene(request, oferta_id):
    if request.method == "POST":
        oferta = get_object_or_404(Oferta, id=oferta_id)
        kwota = safe_float(request.POST.get("kwota"))
        data = request.POST.get("data")
        if kwota is not None and data:
            Cena.objects.create(oferta=oferta, kwota=kwota, data=data)
            return JsonResponse({"status": "success"})
    return JsonResponse({"status": "fail"}, status=400)


# --- Pomocnicza funkcja do bezpiecznej konwersji kwoty ---
def safe_float(value):
    """
    Konwertuje wartość na float, usuwa spacje i przecinki.
    Zwraca None jeśli konwersja się nie powiedzie.
    """
    if value is None:
        return None
    try:
        return float(str(value).replace(" ", "").replace(",", ""))
    except (ValueError, TypeError):
        return None

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from oferty.models import Oferta
import json

@api_view(['GET'])
@permission_classes([AllowAny])
def raport_jsonl(request):
    dane_dewelopera = {
        "nip": "8261116680",
        "regon": "540649478",
        "nazwa_firmy": "B.Z-BUD Beata Żochowska",
        "adres_biura": "woj. MAZOWIECKIE, pow. wołomiński, gm. Zielonka, miejsc. Zielonka, ul. Ignacego Paderewskiego, nr 61, 05-220"
    }

    oferty = Oferta.objects.prefetch_related(
        "ceny", "inwestycja", "pomieszczenia_przynalezne", "rabaty", "inne_swiadczenia"
    ).all()

    raport_lines = []
    for oferta in oferty:
        if not oferta.inwestycja or not oferta.inwestycja.unikalny_identyfikator_przedsiewziecia:
            continue
        ceny_list = list(oferta.ceny.all())
        if not ceny_list:
            continue
        ostatnia_cena = ceny_list[-1]
        cena_m2 = round(float(ostatnia_cena.kwota)/float(oferta.metraz),2) if oferta.metraz else None

        rekord_oferty = {
            "deweloper": dane_dewelopera,
            "inwestycja": {
                "unikalny_identyfikator": oferta.inwestycja.unikalny_identyfikator_przedsiewziecia,
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
                "data_ceny": ostatnia_cena.data.isoformat() if ostatnia_cena else None
            }
        }
        raport_lines.append(rekord_oferty)

    return Response(raport_lines)

