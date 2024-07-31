from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import User
from .resources import UserResource

@admin.register(User)
class UserResource(ImportExportModelAdmin):
    resource_class = UserResource
    list_display = ('email', 'nombre', 'apellido', 'password')