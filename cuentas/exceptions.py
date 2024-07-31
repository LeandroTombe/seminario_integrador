from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed
from django.http import JsonResponse

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, AuthenticationFailed):
        return JsonResponse({'detail': 'Tu mensaje personalizado de error de autentisadasdcación.'}, status=401)

    return response