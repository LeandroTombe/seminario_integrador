from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import AuthenticationFailed

class CustomAuthMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, AuthenticationFailed):
            response = JsonResponse({'detail': 'Tu mensaje personalizado de error de autenticación.'}, status=401)
            return response
        return None