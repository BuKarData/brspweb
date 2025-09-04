from django.http import HttpResponse, JsonResponse
from datetime import datetime

def data_api_view(request):
    if request.path.endswith('.jsonld'):
        data = {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "name": "Testowe dane",
            "dateModified": datetime.now().strftime('%Y-%m-%d'),
            "test": "działa"
        }
        response = JsonResponse(data)
        response['Content-Type'] = 'application/ld+json'
        return response
    
    return HttpResponse('Endpoint testowy', status=200)