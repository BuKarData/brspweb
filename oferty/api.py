from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from .raportuj import generate_jsonld_data, generate_csv_data, generate_xlsx_data
import json

class PlainJSONRenderer(JSONRenderer):
    """Renderer który zawsze zwraca JSON, bez interfejsu HTML"""
    media_type = 'application/json'
    format = 'json'

class DataAPIView(APIView):
    # Użyj naszego renderera zamiast domyślnego
    renderer_classes = [PlainJSONRenderer]
    
    def get(self, request, *args, **kwargs):
        try:
            # Dla JSON-LD
            if request.path.endswith('.jsonld'):
                data = generate_jsonld_data()
                # Zwróć Response z właściwym content-type
                return Response(
                    data,
                    content_type='application/ld+json',
                    headers={'Last-Modified': self.get_current_timestamp()}
                )
            
            # Dla CSV - zwracamy HttpResponse zamiast Response
            elif request.path.endswith('.csv'):
                data = generate_csv_data()
                response = HttpResponse(data, content_type='text/csv')
                response['Content-Disposition'] = 'inline; filename="raport.csv"'
                response['Last-Modified'] = self.get_current_timestamp()
                return response
            
            # Dla XLSX - zwracamy HttpResponse zamiast Response
            elif request.path.endswith('.xlsx'):
                data = generate_xlsx_data()
                response = HttpResponse(
                    data,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'inline; filename="raport.xlsx"'
                response['Last-Modified'] = self.get_current_timestamp()
                return response
            
            return Response({'error': 'Format not supported'}, status=400)
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    def get_current_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')