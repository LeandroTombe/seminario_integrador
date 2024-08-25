from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from import_export import resources, fields
from estudiantes.models import Alumno
from django.contrib.auth.models import Group

User = get_user_model()

class UserResource(resources.ModelResource):
    password = fields.Field(attribute='password', column_name='password')
    legajo = fields.Field(attribute='legajo', column_name='legajo')
    nombre = fields.Field(attribute='nombre', column_name='nombre')
    apellido = fields.Field(attribute='apellido', column_name='apellido')
    documento = fields.Field(attribute='documento', column_name='documento')
    telefono = fields.Field(attribute='telefono', column_name='telefono')
    email = fields.Field(attribute='email', column_name='email')
    dni = fields.Field(attribute='dni', column_name='dni')
    group = fields.Field(attribute='group', column_name='group')

    class Meta:
        model = User
        export_order = ('legajo', 'nombre', 'apellido', 'password','telefono', 'dni', 'group')

    def before_import_row(self, row, **kwargs,):
        legajo = row.get('legajo')
        
        password = row['legajo']
        row['password'] = password
        row['is_active'] = True
        row['group'] = 'alumno'