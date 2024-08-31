from django.shortcuts import render

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from cuentas.permissions import IsAlumno
from rest_framework import status

from .models import Materia, Cuota, Alumno, Cursado, ParametrosCompromiso, FirmaCompromiso, Pago, Inhabilitation, Coordinador, Mensajes
from .serializers import MateriaSerializer, CuotaSerializer, AlumnoSerializer, CursadoSerializer, ParametrosCompromisoSerializer, FirmaCompromisoSerializer, PagoSerializer, InhabilitationSerializer, CoordinadorSerializer, MensajesSerializer
from datetime import datetime

from django.db import IntegrityError

from .utils import alta_cuotas, saldo_vencido, proximo_vencimiento

class MateriasView(APIView):
    permission_classes = [IsAuthenticated, IsAlumno]

    def get(self, request, *args, **kwargs):
        # Lógica para listar materias
        return Response({"message": "Acceso permitido a materias para Alumno"}, status=200)

#Crud de materia


#creacion de materia
class MateriaCreateView(generics.CreateAPIView):
    queryset = Materia.objects.all()
    serializer_class = MateriaSerializer
    permission_classes = [IsAuthenticated, IsAlumno]

#listado de materias

class MateriaListView(generics.ListAPIView):
    queryset = Materia.objects.all()
    serializer_class = MateriaSerializer
    permission_classes = [IsAuthenticated, IsAlumno]

#actualizacion de materia
class MateriaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Materia.objects.all()
    serializer_class = MateriaSerializer
    permission_classes = [IsAuthenticated, IsAlumno]
    
#crud de pagos

class PagoListCreateView(generics.ListCreateAPIView):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    
    
class PagoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    
class AllPagoListView(generics.ListAPIView):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    
class PagoUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    partial = True
    
    
class PagoDeleteView(generics.DestroyAPIView):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(print("Pago eliminado"))

class ParametrosCompromisoSetValores(APIView):
    #permission_classes = [IsAuthenticated, IsAlumno]    #Cambiar rol
    
    def post(self, request, *args, **kwargs):

        serializer=ParametrosCompromisoSerializer(data=request.data)

        if serializer.is_valid():
            parametros = serializer.save()
            return Response({"message": "Compromiso de pago dado de alta"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CompromisoActualView(APIView):

    def get(self, request, *args, **kwargs):
        
        if 3 <= datetime.now().month <= 7:
            cuatrimestre = 1
        else:
            cuatrimestre = 2

        queryset = ParametrosCompromiso.objects.filter(año=datetime.now().year, cuatrimestre=cuatrimestre)    # Buscar forma de filtrar el compromiso actual
        serializer = ParametrosCompromisoSerializer(queryset, many=True)

        if queryset:
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

class AllCompromisoListView(APIView):
    
    def get(self, request, *args, **kwargs):
        queryset = ParametrosCompromiso.objects.all()
        serializer = ParametrosCompromisoSerializer(queryset, many=True)
        
        if queryset:
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

class ParametrosCompromisoEditar(APIView):
    def put(self, request, *args, **kwargs):
        año = request.data.get('año')  # Obtener el año desde los datos de la solicitud
        cuatrimestre = request.data.get('cuatrimestre')

        if not año:
            return Response({"error": "El año es requerido"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            compromiso = ParametrosCompromiso.objects.get(año=año, cuatrimestre=cuatrimestre)  # Encuentra el compromiso existente
        except ParametrosCompromiso.DoesNotExist:
            return Response({"error": "Compromiso de pago no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ParametrosCompromisoSerializer(compromiso, data=request.data, partial=True)  # Usar partial=True para permitir actualizaciones parciales

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Compromiso de pago actualizado exitosamente"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Da de alta la firma de un compromiso de pago por un alumno
class FirmarCompromisoView(APIView):
    permission_classes = [IsAuthenticated] # IsAlumno

    def post(self, request):
        user = request.user  # Obtén el usuario autenticado
        año = request.data.get('año')  # Obtener el año desde los datos de la solicitud
        cuatrimestre = request.data.get('cuatrimestre')

        try:
            alumno = Alumno.objects.get(user=user)  # Busca el alumno relacionado con el usuario autenticado
            parametros_compromiso = ParametrosCompromiso.objects.get(año=año, cuatrimestre=cuatrimestre)

            # Crear y guardar la firma del compromiso
            firma_compromiso = FirmaCompromiso(
                alumno=alumno,
                parametros_compromiso=parametros_compromiso,
            )
            firma_compromiso.save()

            # Llamar a la función para dar de alta las cuotas después de firmar el compromiso
            alta_cuotas(alumno, parametros_compromiso)

            return Response({"message": "Compromiso firmado y cuotas creadas exitosamente"}, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({"error": "El compromiso ya ha sido firmado anteriormente."}, status=status.HTTP_400_BAD_REQUEST)
        except Alumno.DoesNotExist:
            return Response({"error": "El alumno no existe."}, status=status.HTTP_400_BAD_REQUEST)
        except ParametrosCompromiso.DoesNotExist:
            return Response({"error": "El compromiso de pago no existe."}, status=status.HTTP_400_BAD_REQUEST)

# Determina si un alumno ya firmó o no el compromiso de pago actual
class ExistenciaDeFirmaAlumnoCompromisoActualView(APIView):
    def get(self, request):
        user = request.user

        # Determinar el cuatrimestre actual
        if 3 <= datetime.now().month <= 7:
            cuatrimestre = 1
        else:
            cuatrimestre = 2

        try:
            # Buscar el alumno relacionado con el usuario autenticado
            alumno = Alumno.objects.get(user=user)

            # Obtener los parámetros del compromiso de pago para el año y cuatrimestre actuales
            parametros_compromiso = ParametrosCompromiso.objects.get(año=datetime.now().year, cuatrimestre=cuatrimestre)
        
            # Verificar si existe una firma del alumno para el compromiso de pago actual
            firma_existe = FirmaCompromiso.objects.filter(alumno=alumno, parametros_compromiso=parametros_compromiso).exists()

            return Response({"firmado": firma_existe}, status=status.HTTP_200_OK)
        
        except Alumno.DoesNotExist:
            return Response({"error": "El alumno no existe."}, status=status.HTTP_400_BAD_REQUEST)
        except ParametrosCompromiso.DoesNotExist:
            return Response({"error": "El compromiso de pago no existe."}, status=status.HTTP_400_BAD_REQUEST)

# Listar los alumnos que firmaron un compormiso de pago
class FirmaCompromisoActualListView(APIView):
    
    def get(self, request, *args, **kwargs):

        if 3 <= datetime.now().month <= 7:
            cuatrimestre = 1
        else:
            cuatrimestre = 2
        
        # Obtener el último compromiso de pago
        compromiso = ParametrosCompromiso.objects.filter(año=datetime.now().year, cuatrimestre=cuatrimestre).last()
        
        if not compromiso:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # Filtrar los firmantes del compromiso actual
        queryset = FirmaCompromiso.objects.filter(parametros_compromiso=compromiso)
        serializer = FirmaCompromisoSerializer(queryset, many=True)
        
        return Response(serializer.data)


class EstadoDeCuentaAlumnoView(APIView):
    permission_classes = [IsAuthenticated] # IsAlumno

    def get(self, request):
        user = request.user  # Obtén el usuario autenticado
        try:
            alumno = Alumno.objects.get(user=user)  # Busca el alumno relacionado con el usuario autenticado
            queryset = Cuota.objects.filter(alumno=alumno, año=datetime.now().year)
            serializer = CuotaSerializer(queryset, many=True)
            return Response(serializer.data)

        except Alumno.DoesNotExist:
            return Response({"error": "El alumno no existe."}, status=status.HTTP_400_BAD_REQUEST)

class ResumenAlumnoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            alumno = Alumno.objects.get(user=user)
            
            saldo_vencido_resultado = saldo_vencido(alumno)
            proximo_vencimiento_resultado = proximo_vencimiento(alumno)

            return Response({
                "saldoVencido": saldo_vencido_resultado,
                "proximaFechaVencimiento": proximo_vencimiento_resultado
            }, status=status.HTTP_200_OK)
        
        except Alumno.DoesNotExist:
            return Response({"error": "El alumno no existe."}, status=status.HTTP_400_BAD_REQUEST)