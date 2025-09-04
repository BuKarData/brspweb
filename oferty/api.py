from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
import json
from datetime import datetime
from openpyxl import Workbook
import csv
import io

class DataAPIView(APIView):
    def get(self, request, format=None):
        # Generuj dane w różnych formatach
        data = self.generate_data()
        
        if format == 'jsonld' or request.path.endswith('.jsonld'):
            return Response(
                data['jsonld'],
                content_type='application/ld+json',
                headers={'Last-Modified': datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')}
            )
        elif format == 'csv' or request.path.endswith('.csv'):
            response = HttpResponse(data['csv'], content_type='text/csv')
            response['Content-Disposition'] = 'inline; filename="data.csv"'
            response['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
            return response
        elif format == 'xlsx' or request.path.endswith('.xlsx'):
            response = HttpResponse(
                data['xlsx'],
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'inline; filename="data.xlsx"'
            response['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
            return response
        else:
            return Response({'error': 'Unsupported format'}, status=400)
    
    def generate_data(self):
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Przykładowe dane - ZASTĄP TYM SWOJĄ LOGIKĄ z raportuj.py
        sample_data = [
            {'id': 1, 'name': 'Przykład 1', 'value': 100, 'date': current_date},
            {'id': 2, 'name': 'Przykład 2', 'value': 200, 'date': current_date},
        ]
        
        # Generuj JSON-LD
        jsonld_data = {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "name": "Raport danych",
            "description": "Automatycznie generowany raport danych",
            "dateModified": current_date,
            "variables": [
                {
                    "@type": "PropertyValue",
                    "name": item['name'],
                    "value": item['value'],
                    "date": item['date']
                } for item in sample_data
            ]
        }
        
        # Generuj CSV
        csv_output = io.StringIO()
        csv_writer = csv.writer(csv_output)
        csv_writer.writerow(['ID', 'Name', 'Value', 'Date'])  # Nagłówki
        for item in sample_data:
            csv_writer.writerow([item['id'], item['name'], item['value'], item['date']])
        csv_content = csv_output.getvalue()
        csv_output.close()
        
        # Generuj XLSX
        wb = Workbook()
        ws = wb.active
        ws.title = "Dane"
        ws.append(['ID', 'Name', 'Value', 'Date'])  # Nagłówki
        for item in sample_data:
            ws.append([item['id'], item['name'], item['value'], item['date']])
        
        xlsx_output = io.BytesIO()
        wb.save(xlsx_output)
        xlsx_content = xlsx_output.getvalue()
        xlsx_output.close()
        
        return {
            'jsonld': jsonld_data,
            'csv': csv_content,
            'xlsx': xlsx_content
        }