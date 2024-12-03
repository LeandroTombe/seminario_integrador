from rest_framework import serializers
from django.db.models import F
from datetime import datetime
from django.contrib.auth import get_user_model


from .models import Notificacion,Materia,Cuota,Alumno,Cursado,ParametrosCompromiso,FirmaCompromiso,Pago,Inhabilitation,Coordinador,DetallePago,SolicitudProrroga, SolicitudBajaProvisoria, Mensaje, RespuestaMensaje
from cuentas.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('nombre', 'apellido', 'group', 'documento', 'legajo')

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
        model = Mensaje
        fields = ('alumno', 'periodo', 'fechaFirma')
        
class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = ['id', 'alumno', 'tipo_evento', 'mensaje', 'fecha', 'visto']
        
class Cuota2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Cuota
        fields = ['id', 'importe', 'importePagado', 'fechaPrimerVencimiento']

class AlumnosCoutasNoPagadas(serializers.ModelSerializer):
    ultima_cuota_pagada = serializers.SerializerMethodField()
    cuotas_vencidas = serializers.SerializerMethodField()  # Campo para cuotas vencidas

    class Meta:
        model = Alumno
        fields = ['id', 'legajo', 'email', 'nombre', 'apellido', 'dni', 'pago_al_dia', 'ultima_cuota_pagada', 'cuotas_vencidas']

    def get_ultima_cuota_pagada(self, obj):
        # Obtener la última cuota pagada para el alumno
        cuotas_pagadas = Cuota.objects.filter(alumno=obj, total=F('importePagado')).order_by('-nroCuota')
        if cuotas_pagadas.exists():
            ultima_cuota_pagada = cuotas_pagadas.first()
            # Obtener el mes del primer vencimiento
            mes_numero = ultima_cuota_pagada.nroCuota
            # Usar la función tratarFecha para convertir el número del mes en el nombre
            return tratarFecha(mes_numero)
        
        return None

    def get_cuotas_vencidas(self, obj):
        # Obtener las cuotas vencidas para el alumno
        hoy = datetime.now()
        cuotas_vencidas = Cuota.objects.filter(
            alumno=obj,
            total__gt=F('importePagado'),  # Cuota no completamente pagada
            fechaPrimerVencimiento__lt=hoy  # Fecha de vencimiento en el pasado
        )
        nombre_cuotas_vencidas = []
        for cuota in cuotas_vencidas:
            nombre_cuotas_vencidas.append(tratarFecha(cuota.nroCuota))
        return nombre_cuotas_vencidas

def tratarFecha(mes):
    meses = {
        0: "Matricula",
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

class SolicitudProrrogaSerializer(serializers.ModelSerializer):
    alumno = AlumnoSerializer()
    materia = MateriaSerializer()
    
    class Meta:
        model = SolicitudProrroga
        fields = ['id', 'alumno', 'materia', 'analitico', 'motivo', 'estado', 'fecha_solicitud', 'comentarios', 'fecha_evaluacion']
        read_only_fields = ['estado', 'fecha_solicitud']

class SolicitudBajaProvisoriaSerializer(serializers.ModelSerializer):
    alumno = AlumnoSerializer()
    compromiso = ParametrosCompromisoSerializer()

    class Meta:
        model = SolicitudBajaProvisoria
        fields = ['id', 'alumno', 'compromiso', 'motivo', 'estado', 'fecha_solicitud', 'comentarios', 'fecha_evaluacion']

User = get_user_model()

class MensajeSerializer(serializers.ModelSerializer):
    remitente = UserSerializer()
    destinatario = UserSerializer(
        many=True
    )
    leido_por = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True
    )

    class Meta:
        model = Mensaje
        fields = [
            "id",
            "remitente",
            "destinatario",
            "asunto",
            "contenido",
            "fecha_envio",
            "mensaje_grupal",
            "leido_por",
        ]
        read_only_fields = ["remitente", "fecha_envio"]

    def validate(self, data):
        request = self.context.get("request")
        if request.user.group == "alumno":
            # Verificar que los destinatarios sean solo coordinadores
            for destinatario in data["destinatario"]:
                if destinatario.group != "coordinador":
                    raise serializers.ValidationError(
                        "Los alumnos solo pueden enviar mensajes a coordinadores."
                    )
        return data

class RespuestaMensajeSerializer(serializers.ModelSerializer):
    remitente = serializers.StringRelatedField(read_only=True)
    mensaje_original = serializers.PrimaryKeyRelatedField(
        queryset=Mensaje.objects.all()
    )

    class Meta:
        model = RespuestaMensaje
        fields = ["id", "mensaje_original", "remitente", "contenido", "fecha_envio"]
        read_only_fields = ["remitente", "fecha_envio"]

    def validate(self, data):
        request = self.context.get("request")
        mensaje_original = data["mensaje_original"]
        # Validar que el remitente sea parte de la conversación
        if request.user != mensaje_original.remitente and request.user not in mensaje_original.destinatario.all():
            raise serializers.ValidationError(
                "No tienes permiso para responder este mensaje."
            )
        return data