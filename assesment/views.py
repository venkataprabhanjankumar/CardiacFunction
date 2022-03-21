from django.http.response import HttpResponse
import json
from rest_framework.decorators import api_view


@api_view(['POST'])
def get_result(request):
    print(request.FILES)
    echo_video = request.FILES.get('echovideo')
    return HttpResponse(json.dumps({'status': 'ok'}))
