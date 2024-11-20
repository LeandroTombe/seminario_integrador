from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Peticionesservidor
import json

def ejecutar_peticion_view(request):
    if request.method == 'GET':
        try:
            # Obtener el legajo del estudiante desde los parámetros de la URL
            legajo = request.GET.get("legajo")
            if not legajo:
                return JsonResponse({
                    "success": False,
                    "error": "El legajo es obligatorio"
                }, status=400)

            # Obtener el tipo de la petición desde los parámetros de la URL
            tipo_peticion = request.GET.get("tipo_peticion")
            if not tipo_peticion:
                return JsonResponse({
                    "success": False,
                    "error": "El tipo de petición es obligatorio"
                }, status=400)

            # Convertir tipo_peticion a un valor entero
            tipo_peticion = int(tipo_peticion)

            # Crear la instancia de Peticionesservidor
            peticion = Peticionesservidor()

            # Establecer el ID usando el legajo
            peticion.set_Id(legajo)

            # Añadir el parámetro 'legajo'
            peticion.add_parametro('legajo', legajo)

            # Ejecutar la petición
            error, param2, param3 = peticion.ejecutar_peticion(tipo_peticion)

            # Si no hay error, devolver los datos
            if not error:
                return JsonResponse({
                    "success": True,
                    "data": {
                        "parametro2": param2,
                        "parametro3": param3,
                    }
                }, status=200)
            else:
                return JsonResponse({
                    "success": False,
                    "error": error
                }, status=500)

        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=500)

    return JsonResponse({
        "success": False,
        "error": "Método HTTP no permitido"
    }, status=405)
