from django.contrib import admin

from auditar.models import Auditoria

# Register your models here.


@admin.register(Auditoria)
class Auditoria(admin.ModelAdmin):
    pass