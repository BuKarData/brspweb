from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
import json

# Modele danych zgodne z ustawą
class Adres(BaseModel):
    wojewodztwo: str = Field(..., description="Nazwa województwa")
    powiat: str = Field(..., description="Nazwa powiatu")
    gmina: str = Field(..., description="Nazwa gminy")
    miejscowosc: str = Field(..., description="Nazwa miejscowości")
    ulica: Optional[str] = Field(None, description="Nazwa ulicy")
    numerDomu: Optional[str] = Field(None, description="Numer domu")
    numerLokalu: Optional[str] = Field(None, description="Numer lokalu")
    kodPocztowy: str = Field(..., description="Kod pocztowy")

class Wspolrzedne(BaseModel):
    szerokoscGeograficzna: float = Field(..., description="Szerokość geograficzna")
    dlugoscGeograficzna: float = Field(..., description="Długość geograficzna")

class OfertaNieruchomosci(BaseModel):
    id: str = Field(..., description="Unikalny identyfikator oferty")
    typOferty: str = Field(..., description="Typ oferty: sprzedaż/wynajem")
    typNieruchomosci: str = Field(..., description="Typ nieruchomosci: mieszkanie/dom/dzialka")
    cena: float = Field(..., description="Cena nieruchomosci")
    waluta: str = Field(..., description="Waluta", default="PLN")
    powierzchnia: float = Field(..., description="Powierzchnia w m²")
    liczbaPokoi: Optional[int] = Field(None, description="Liczba pokoi")
    pietro: Optional[int] = Field(None, description="Piętro")
    liczbaPieter: Optional[int] = Field(None, description="Liczba pięter w budynku")
    rokBudowy: Optional[int] = Field(None, description="Rok budowy")
    stanNieruchomosci: Optional[str] = Field(None, description="Stan nieruchomosci")
    opis: Optional[str] = Field(None, description="Opis nieruchomosci")
    adres: Adres = Field(..., description="Adres nieruchomosci")
    wspolrzedne: Optional[Wspolrzedne] = Field(None, description="Współrzędne geograficzne")
    dataDodania: date = Field(..., description="Data dodania oferty")
    dataAktualizacji: date = Field(..., description="Data aktualizacji oferty")
    linkDoOferty: str = Field(..., description="Link do oryginalnej oferty")

class ZbiorOfert(BaseModel):
    oferty: List[OfertaNieruchomosci] = Field(..., description="Lista ofert nieruchomosci")
    dataGenerowania: date = Field(..., description="Data generowania zbioru")
    zrodlo: str = Field(..., description="Źródło danych")

app = FastAPI(
    title="API Raportowania Cen Mieszkań",
    description="API do raportowania danych zgodnie z ustawą o jawnych cenach mieszkań w Polsce",
    version="1.0.0"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Dodajemy przykładowe odpowiedzi
    openapi_schema["components"]["schemas"]["ZbiorOfert"]["example"] = {
        "oferty": [
            {
                "id": "OFERTA_001",
                "typOferty": "sprzedaż",
                "typNieruchomosci": "mieszkanie",
                "cena": 450000.0,
                "waluta": "PLN",
                "powierzchnia": 65.5,
                "liczbaPokoi": 3,
                "pietro": 2,
                "liczbaPieter": 5,
                "rokBudowy": 2010,
                "stanNieruchomosci": "bardzo dobry",
                "opis": "Przestronne mieszkanie w centrum miasta",
                "adres": {
                    "wojewodztwo": "mazowieckie",
                    "powiat": "Warszawa",
                    "gmina": "Warszawa",
                    "miejscowosc": "Warszawa",
                    "ulica": "Marszałkowska",
                    "numerDomu": "123",
                    "numerLokalu": "45",
                    "kodPocztowy": "00-001"
                },
                "wspolrzedne": {
                    "szerokoscGeograficzna": 52.2297,
                    "dlugoscGeograficzna": 21.0122
                },
                "dataDodania": "2024-01-15",
                "dataAktualizacji": "2024-01-15",
                "linkDoOferty": "https://example.com/oferta/1"
            }
        ],
        "dataGenerowania": "2024-01-15",
        "zrodlo": "BRSP Web Scraper"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/")
async def root():
    return {"message": "BRSP Web API - Raportowanie cen mieszkań"}

@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_endpoint():
    return app.openapi()

@app.post("/api/raport", response_model=ZbiorOfert)
async def utworz_raport(zbior_ofert: ZbiorOfert):
    """
    Endpoint do tworzenia raportu ofert nieruchomości.
    
    Przyjmuje zbiór ofert w formacie JSON i zwiera potwierdzenie przyjęcia danych.
    """
    # Tutaj dodaj logikę zapisywania danych do bazy lub pliku
    try:
        # Zapisz dane - możesz użyć Twojej istniejącej funkcji z raportuj.py
        from raportuj import zapisz_raport_json
        
        # Konwersja do dict dla kompatybilności
        dane_do_zapisu = zbior_ofert.dict()
        zapisz_raport_json(dane_do_zapisu, "raport_api.json")
        
        return zbior_ofert
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas przetwarzania raportu: {str(e)}")

@app.get("/api/oferty", response_model=ZbiorOfert)
async def pobierz_oferty(data_od: Optional[date] = None, data_do: Optional[date] = None):
    """
    Endpoint do pobierania ofert nieruchomości z określonego okresu.
    """
    try:
        # Tutaj dodaj logikę wczytywania danych z bazy lub plików
        # Na razie zwracamy przykładowe dane
        from datetime import datetime
        from raportuj import wczytaj_raport_json
        
        # Próba wczytania istniejących danych
        try:
            dane = wczytaj_raport_json("raport_api.json")
            return ZbiorOfert(**dane)
        except:
            # Jeśli nie ma danych, zwróć przykładowe
            return ZbiorOfert(
                oferty=[],
                dataGenerowania=datetime.now().date(),
                zrodlo="BRSP Web API"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas pobierania ofert: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)