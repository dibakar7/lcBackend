# CommonLawCratsBackend/views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def home(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse JSON data
            print(data)
            response_data = {'message': 'Data received', 'received_data': data}
            return JsonResponse(response_data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'message': 'Send a POST request'}, status=405)


