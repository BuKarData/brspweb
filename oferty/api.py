# oferty/api.py - PROSTA WERSJA TESTOWA
from django.http import JsonResponse
from datetime import datetime

def simple_api_test(request):
    """Prosta funkcja testowa bez złożonych importów"""
    data = {
        "test": "działa",
        "timestamp": datetime.now().isoformat(),
        "message": "API test successful"
    }
    return JsonResponse(data)