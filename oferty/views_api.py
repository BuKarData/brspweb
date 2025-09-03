# oferty/views_api.py
from rest_framework.views import APIView
from rest_framework.response import Response

class RaportList(APIView):
    def get(self, request):
        # przykładowe dane
        return Response([{"id": 1, "nazwa": "Oferta A"}])
