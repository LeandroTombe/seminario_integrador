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
        user = User.objects.get(email=row['email'])
        user.set_password(row['password'])
        user.save()

        group, _ = Group.objects.get_or_create(name='Alumno')
        user.groups.add(group)

        # Crear o actualizar el modelo Alumno
        Alumno.objects.update_or_create(
            legajo=row.get('legajo'),
            defaults={
                'nombre': row.get('nombre'),
                'apellido': row.get('apellido'),
                'telefono': row.get('telefono'),
                'email': row.get('email'),
                'dni': row.get('dni')
            }
        )