import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificacionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.alumno_group_name = f'notificaciones_{self.user.id}'

        # Únete al grupo de WebSocket para este alumno
        await self.channel_layer.group_add(
            self.alumno_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Sal del grupo cuando se desconecta
        await self.channel_layer.group_discard(
            self.alumno_group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        message = event['message']

        # Envía el mensaje de notificación al WebSocket
        await self.send(text_data=json.dumps({
            'mensaje': message['mensaje'],
            'fecha': message['fecha']
        }))