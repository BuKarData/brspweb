from django.http import HttpResponse, JsonResponse
from datetime import datetime
from oferty.management.commands.raportuj import (
    generate_jsonld_data, 
    generate_csv_data, 
    generate_xlsx_data
)

def data_api_view(request):
    try:
        if request.path.endswith('.jsonld'):
            data = generate_jsonld_data()
            response = JsonResponse(data, json_dumps_params={'ensure_ascii': False})
            response['Content-Type'] = 'application/ld+json'
            
        elif request.path.endswith('.csv'):
            data = generate_csv_data()
            if not data or data == "":
                return HttpResponse('No CSV data available', status=404, content_type='text/plain')
            response = HttpResponse(data, content_type='text/csv')
            response['Content-Disposition'] = 'inline; filename="raport.csv"'
            
        elif request.path.endswith('.xlsx'):
            data = generate_xlsx_data()
            if not data:
                return HttpResponse('No XLSX data available', status=404, content_type='text/plain')
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