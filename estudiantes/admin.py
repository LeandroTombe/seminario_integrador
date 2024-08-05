from django.contrib import admin

from .models import Materia, Alumno,Pago

# Register your models here.


admin.site.register(Materia)

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ('legajo', 'telefono', 'dni')

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('alumno', 'monto_informado', 'fecha_pago_informado', 'monto_confirmado', 'fecha_pago_confirmado', 'forma_pago')
    list_filter = ('forma_pago', 'fecha_pago_informado', 'fecha_pago_confirmado')
    search_fields = ('alumno__nombre', 'alumno__apellido')