from datetime import datetime
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from auditar.serializers import AuditoriaSerializer
from .models import Auditoria
from rest_framework import generics

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

def crear_auditoria(accion, detalles=None):
    """
    Crea una entrada de auditoría para el objeto dado.
    
    :param objeto: Instancia del modelo que se va a auditar
    :param accion: Descripción de la acción a auditar (ej. 'Creación', 'Modificación')
    """
    #content_type = ContentType.objects.get_for_model(objeto)
    cuatrimestre_actual = 1 if timezone.now().month <= 8 else 2
    print(detalles)
    # Crear la entrada de auditoría
    Auditoria.objects.create(
        año=timezone.now().year,
        cuatrimestre=cuatrimestre_actual,
        #content_type=content_type,
        #object_id=objeto.id,
        accion=accion,
        detalles=detalles or {}

    )
    

class AuditoriaListView(APIView):
    def get(self, request):
        # Obtener el parámetro 'fecha' de la URL
        fecha_str = request.GET.get('fecha', None)
        
        if fecha_str:
            try:
                # Convertir la fecha del formato 'dd/mm/yyyy' al formato datetime
                fecha_buscada = datetime.strptime(fecha_str, '%d/%m/%Y')
                
                # Definir el rango del día
                fecha_inicio = fecha_buscada.replace(hour=0, minute=0, second=0, microsecond=0)
                fecha_fin = fecha_buscada.replace(hour=23, minute=59, second=59, microsecond=999999)

                # Filtrar las auditorías en ese rango de fechas
                auditorias = Auditoria.objects.filter(
                    fecha__range=[fecha_inicio, fecha_fin]
                )
                
                # Serializar los resultados
                serializer = AuditoriaSerializer(auditorias, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            except ValueError:
                return Response({"error": "Formato de fecha no válido. Use dd/mm/yyyy."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Si no se proporciona 'fecha', devolver todos los registros
        auditorias = Auditoria.objects.all()
        serializer = AuditoriaSerializer(auditorias, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)