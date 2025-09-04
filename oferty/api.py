from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from datetime import datetime
from oferty.management.commands.raportuj import (
    generate_jsonld_data, 
    generate_csv_data, 
    generate_xlsx_data
)

class DataAPIView(APIView):
    # WYŁĄCZ renderery DRF całkowicie dla tego widoku
    renderer_classes = []
    
    def get(self, request, *args, **kwargs):
        try:
            # Dla JSON-LD - używamy JsonResponse zamiast Response
            if request.path.endswith('.jsonld'):
                data = generate_jsonld_data()
                response = JsonResponse(data, json_dumps_params={'ensure_ascii': False})
                response['Content-Type'] = 'application/ld+json'
                response['Last-Modified'] = self.get_current_timestamp()
                return response
            
            # Dla CSV - HttpResponse
            elif request.path.endswith('.csv'):
                data = generate_csv_data()
                response = HttpResponse(data, content_type='text/csv')
                response['Content-Disposition'] = 'inline; filename="raport.csv"'
                response['Last-Modified'] = self.get_current_timestamp()
                return response
            
            # Dla XLSX - HttpResponse
            elif request.path.endswith('.xlsx'):
                data = generate_xlsx_data()
                response = HttpResponse(
                    data,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'inline; filename="raport.xlsx"'
                response['Last-Modified'] = self.get_current_timestamp()
                return response
            
            # Dla nieobsługiwanego formatu
            return HttpResponse('Format not supported', status=400, content_type='text/plain')
            
        except Exception as e:
            return HttpResponse(f'Error: {str(e)}', status=500, content_type='text/plain')
    
    def get_current_timestamp(self):
        return datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')