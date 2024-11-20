from django.urls import path
from .views import ejecutar_peticion_view

urlpatterns = [
    # Otras rutas de tu aplicación
    path('datos-sqlserver/', ejecutar_peticion_view, name='ejecutar_peticion_view'),
]