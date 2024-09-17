from django.urls import path, re_path
from .consumer import NotificacionConsumer

websocket_urlpatterns = [
    path('ws/notificaciones/', NotificacionConsumer.as_asgi()),
]