from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed
from django.http import JsonResponse

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, AuthenticationFailed):
        return JsonResponse({'mensaje': 'No tiene los suficientes permisos para ingresar a esta pagina.'}, status=401)

    return response