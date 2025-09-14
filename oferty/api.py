from django.http import HttpResponse
import json 
from datetime import datetime
from oferty.management.commands.raportuj import (
    generate_jsonld_data, 
    generate_csv_data, 
    generate_xlsx_data
)
from django.http import FileResponse
import os

def metadata_xml(request):
    # Ścieżka do pliku w templates/api/
    xml_file_path = os.path.join(settings.BASE_DIR, 'oferty', 'templates', 'api', 'metadata.xml')
    
    if os.path.exists(xml_file_path):
        return FileResponse(open(xml_file_path, 'rb'), content_type='application/xml')
    else:
        from django.http import HttpResponseNotFound
        return HttpResponseNotFound("Plik metadata.xml nie został jeszcze wygenerowany")



def data_api_view(request):
    try:
        if request.path.endswith('.jsonld'):
            data = generate_jsonld_data()
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            response = HttpResponse(json_data, content_type='application/ld+json; charset=utf-8')
            
        elif request.path.endswith('.csv'):
            data = generate_csv_data()
            # ZMIANA: Użyj BytesIO lub odpowiedniego encodingu
            response = HttpResponse(
                data,
                content_type='text/csv; charset=utf-8'
            )
            response['Content-Disposition'] = 'inline; filename="raport.csv"'
            response['Content-Encoding'] = 'utf-8'
            
        elif request.path.endswith('.xlsx'):
            data = generate_xlsx_data()
            response = HttpResponse(
                data,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'inline; filename="raport.xlsx"'
            
        else:
            return HttpResponse('Format not supported', status=400, content_type='text/plain')
        
        response['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        return response
        
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500, content_type='text/plain')