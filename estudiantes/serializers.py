from rest_framework import serializers
from django.db.models import F



from .models import Notificacion,Materia,Cuota,Alumno,Cursado,ParametrosCompromiso,FirmaCompromiso,Pago,Inhabilitation,Coordinador,Mensajes,DetallePago


class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = ('codigo_materia', 'nombre')

class CuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuota
        fields = ('nroCuota', 'año', 'importe', 'moraPrimerVencimiento', 'fechaPrimerVencimiento', 'moraSegundoVencimiento', 'fechaSegundoVencimiento', 'total', 'importePagado', 'importeInformado', 'fechaImporteInformado', 'estado')

class AlumnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumno
        fields = '__all__'

class CursadoSerializer(serializers.ModelSerializer):
    alumno = AlumnoSerializer()
    materia = MateriaSerializer()

    class Meta:
        model = Cursado
        fields = ('alumno', 'materia', 'año', 'cuatrimestre')

class ParametrosCompromisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParametrosCompromiso
        fields = ('año', 'cuatrimestre', 'compromiso_contenido', 'importe_matricula', 'importe_reducido', 'importe_completo', 'importe_pri_venc_comp', 'importe_pri_venc_red', 'importe_seg_venc_comp', 'importe_seg_venc_red')

class FirmaCompromisoSerializer(serializers.ModelSerializer):
    alumno = AlumnoSerializer()

    class Meta:
        model = FirmaCompromiso
        fields = ('alumno', 'parametros_compromiso' ,'fechaFirma')
        read_only_fields = ['fecha_firma']


class DetallePagoSerializer(serializers.ModelSerializer):
    cuota = CuotaSerializer()

    class Meta:
        model = DetallePago
        fields = ('id', 'cuota', 'monto_cuota')

class PagoSerializer(serializers.ModelSerializer):
    alumno = AlumnoSerializer()
    detalles = DetallePagoSerializer(source='detallepago_set', many=True, read_only=True)
    
    class Meta:
        model = Pago
        fields = ('id', 'numero_recibo', 'alumno', 'monto_confirmado', 'fecha_pago_confirmado', 'comprobante_de_pago', 'forma_pago', 'detalles')
        
        
class InhabilitationSerializer(serializers.ModelSerializer):
    alumno = AlumnoSerializer()

    class Meta:
        model = Inhabilitation
        fields = ('alumno', 'fechaInicio', 'fechaFin', 'motivo', 'tipo')

class CoordinadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinador
        fields = ('codCoor', 'nombre', 'apellido', 'telefono', 'email', 'dni')

class MensajesSerializer(serializers.ModelSerializer):
    alumno = AlumnoSerializer()

    class Meta:
        model = Mensajes
        fields = ('alumno', 'periodo', 'fechaFirma')
        
class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = ['id', 'alumno', 'mensaje', 'fecha']
        
        
class AlumnosCoutasNoPagadas(serializers.ModelSerializer):
    ultima_cuota_pagada = serializers.SerializerMethodField()
    class Meta:
        model = Alumno
        fields = ['id','legajo', 'email','nombre', 'apellido', 'dni', 'pago_al_dia', 'ultima_cuota_pagada']

    def get_ultima_cuota_pagada(self, obj):
        # Obtener la última cuota pagada para el alumno
        cuotas_pagadas = Cuota.objects.filter(alumno=obj, total=F('importePagado')).order_by('-fechaPrimerVencimiento')
        
        if cuotas_pagadas.exists():
            ultima_cuota_pagada = cuotas_pagadas.first()
            # Obtener el mes del primer vencimiento
            mes_numero = ultima_cuota_pagada.fechaPrimerVencimiento.month
            # Usar la función tratarFecha para convertir el número del mes en el nombre
            return tratarFecha(mes_numero)
        
        return None

def tratarFecha(mes):
    meses = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre"
    }
    return meses.get(mes, "Desconocido")