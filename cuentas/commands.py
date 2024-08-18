from django.core.management.base import BaseCommand
from django.contrib.auth.management.commands.createsuperuser import Command as CreateSuperUserCommand
from django.contrib.auth import get_user_model

class Command(CreateSuperUserCommand):
    def handle(self, *args, **options):
        # Llama al método handle original para crear el superusuario
        super().handle(*args, **options)
        
        User = get_user_model()
        email = options['email']
        user = User.objects.get(email=email)

        # Asignar el grupo 'admin' al campo 'group'
        user.group = 'admin'
        user.save()