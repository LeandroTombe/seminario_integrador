from import_export import resources,fields 
from .models import User
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
import environ
from django.contrib.auth.models import Group

User = get_user_model()



# Inicializa environ
env = environ.Env(
    # Establece valores por defecto y convierte a los tipos esperados
    DEBUG=(bool, False)
)
# Lee el archivo .env
environ.Env.read_env(env_file='.env')


class UserResource(resources.ModelResource):
    password = fields.Field(attribute='password', column_name='password')
    
    
    class Meta:
         model = User
         export_order = ( 'email', 'nombre', 'apellido', 'password')
         
    
    def before_import_row(self, row, **kwargs):
        
        email = row.get('email')
        
        # Verificar si el usuario ya existe
        if User.objects.filter(email=email).exists():
            # Marcar la fila para que no se importe
            raise ValueError(f"El usuario con el email {email} ya existe. La fila será ignorada.")
        
        
        # Usar el email como contraseña
        password = row['email']
        row['password'] = password
        row['is_active'] = True

        # Enviar el correo electrónico
        send_mail(
            'Tu nueva contraseña',
            f'Tu nueva contraseña es: {password}',
            'from@example.com',
            [row['email']],
            fail_silently=False,
        )

    def after_import_row(self, row, row_result, **kwargs):
        # Establecer la contraseña del usuario
        user = User.objects.get(email=row['email'])
        user.set_password(row['password'])
        user.save()
        # Asignar el rol "Estudiantes"
        group, _ = Group.objects.get_or_create(name='Alumno')
        user.groups.add(group)

