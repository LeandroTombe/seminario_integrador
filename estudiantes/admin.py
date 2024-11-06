from django.contrib import admin

from .models import Materia, Alumno,Pago, ParametrosCompromiso, FirmaCompromiso, Cuota, DetallePago, SolicitudProrroga, SolicitudBajaProvisoria

# Register your models here.


admin.site.register(Materia)

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ('legajo', 'nombre', 'apellido')

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('alumno', 'monto_confirmado', 'fecha_pago_confirmado', 'forma_pago')
    list_filter = ('forma_pago', 'fecha_pago_confirmado')
    search_fields = ('alumno__nombre', 'alumno__apellido')

@admin.register(ParametrosCompromiso)
class AlumnoAdmin(admin.ModelAdmin):
    pass

@admin.register(FirmaCompromiso)
class AlumnoAdmin(admin.ModelAdmin):
    pass

@admin.register(Cuota)
class AlumnoAdmin(admin.ModelAdmin):
    pass

@admin.register(DetallePago)
class DetallePagoAdmin(admin.ModelAdmin):
    pass

@admin.register(SolicitudProrroga)
class SolicitudProrrogaAdmin(admin.ModelAdmin):
    pass

@admin.register(SolicitudBajaProvisoria)
class SolicitudBajaProvisoriaAdmin(admin.ModelAdmin):
    pass