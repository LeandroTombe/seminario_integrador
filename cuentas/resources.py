from django.core.mail import send_mail
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from import_export import resources, fields
from estudiantes.models import Alumno  # Asegúrate de importar tu modelo Alumno

User = get_user_model()

class UserResource(resources.ModelResource):
    password = fields.Field(attribute='password', column_name='password')
    legajo = fields.Field(attribute='legajo', column_name='legajo')
    nombre = fields.Field(attribute='nombre', column_name='nombre')
    apellido = fields.Field(attribute='apellido', column_name='apellido')
    telefono = fields.Field(attribute='telefono', column_name='telefono')
    email = fields.Field(attribute='email', column_name='email')
    dni = fields.Field(attribute='dni', column_name='dni')

    class Meta:
        model = User
        export_order = ('email', 'nombre', 'apellido', 'password', 'legajo', 'telefono', 'dni')

    def before_import_row(self, row, **kwargs):
        email = row.get('email')

        if User.objects.filter(email=email).exists():
            raise ValueError(f"El usuario con el email {email} ya existe. La fila será ignorada.")

        password = row['email']
        row['password'] = password
        row['is_active'] = True
        """
        send_mail(
            'Tu nueva contraseña',
            f'Tu nueva contraseña es: {password}',
            'from@example.com',
            [row['email']],
            fail_silently=False,
        )
        """
    def after_import_row(self, row, row_result, **kwargs):
        email = row.get('email')
        password = row.get('password')

        try:
            # Validar campos esenciales
            if not all([email, row.get('nombre'), row.get('apellido')]):
                print(f"Fila con email '{email}' tiene campos esenciales faltantes.")
                return

            # Crear o actualizar el usuario
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'nombre': row.get('nombre'),
                    'apellido': row.get('apellido'),
                }
            )

            if not created:
                print(f"El usuario con email '{email}' ya existe. Actualizando información...")

            if password:
                user.set_password(password)
            user.save()

            # Crear o actualizar el modelo Alumno
            alumno_defaults = {
                'legajo': row.get('legajo'),
                'nombre': row.get('nombre'),
                'apellido': row.get('apellido'),
                'telefono': row.get('telefono'),
                'dni': row.get('dni'),
                'user': user,  # Asocia el modelo Alumno con el usuario
            }

            # Asegúrate de que `email` sea único en `Alumno` o usa otro campo único
            Alumno.objects.update_or_create(
                email=email,
                defaults=alumno_defaults
            )
           

            print(f"Usuario con email '{email}' procesado correctamente.")
        except Exception as e:
            print(f"Error al importar fila con email '{email}': {str(e)}")