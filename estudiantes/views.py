import calendar
from decimal import Decimal
from django.shortcuts import get_object_or_404, render

import pandas as pd
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view
from unidecode import unidecode
from cuentas.permissions import IsAlumno
from rest_framework import status

from .models import DetallePago, Materia, Cuota, Alumno, Cursado, ParametrosCompromiso, FirmaCompromiso, Pago, Inhabilitation, Coordinador, Mensajes, SolicitudProrroga
from .serializers import AlumnosCoutasNoPagadas, MateriaSerializer, CuotaSerializer, AlumnoSerializer, CursadoSerializer, NotificacionSerializer, ParametrosCompromisoSerializer, FirmaCompromisoSerializer, PagoSerializer, InhabilitationSerializer, CoordinadorSerializer, MensajesSerializer, SolicitudProrrogaSerializer
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import now


from django.db import IntegrityError
from django.db.models import Q,F

from .models import Notificacion
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .utils import alta_cuotas, saldo_vencido, proximo_vencimiento

from datetime import datetime

#pruebas 
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

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
    queryset = Pago.objects.all().order_by('-id')
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

class AllAlumnosInscriptosListView(APIView):
    def get(self, request, *args, **kwargs):

        # Aca hacer el control de que esten inscriptos este cuatrimestre!
        queryset = Alumno.objects.all().order_by('apellido')
        serializer = AlumnoSerializer(queryset, many=True)
        
        return Response(serializer.data)

class ParametrosCompromisoSetValores(APIView):
    #permission_classes = [IsAuthenticated, IsAlumno]    #Cambiar rol
    
    # filtar por año y cuatrimestre, en caso que exista, devolver error
    def get(self, request, *args, **kwargs):
        año = request.GET.get('año')
        cuatrimestre = request.GET.get('cuatrimestre')
         
        # buscar si ya existe un compromiso para ese año y cuatrimestre
        queryset = ParametrosCompromiso.objects.filter(año=año, cuatrimestre=cuatrimestre)
        serializer = ParametrosCompromisoSerializer(queryset, many=True)
        # en caso de que exista, devolver error
        if queryset:
            return Response({"error": "Ya existe un compromiso para el año y cuatrimestre especificados"}, status=status.HTTP_200_OK)
        
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, *args, **kwargs):
        
        #agregar el get de año y cuatrimestre
        
        año = request.data.get('año')
        cuatrimestre = request.data.get('cuatrimestre')
        
        if ParametrosCompromiso.objects.filter(año=año, cuatrimestre=cuatrimestre).exists():
            return Response({"error": "Ya existe un compromiso para el año y cuatrimestre especificados"}, status=status.HTTP_400_BAD_REQUEST)
        

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

            # Llamar a la función para dar de alta las cuotas después de firmar el compromiso
            alta_cuotas(alumno, parametros_compromiso)

            # Crear y guardar la firma del compromiso
            firma_compromiso = FirmaCompromiso(
                alumno=alumno,
                parametros_compromiso=parametros_compromiso,
            )
            firma_compromiso.save()

            return Response({"message": "Compromiso firmado y cuotas creadas exitosamente"}, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({"error": "El compromiso ya ha sido firmado anteriormente."}, status=status.HTTP_400_BAD_REQUEST)
        except Alumno.DoesNotExist:
            return Response({"error": "El alumno no existe."}, status=status.HTTP_400_BAD_REQUEST)
        except ParametrosCompromiso.DoesNotExist:
            return Response({"error": "El compromiso de pago no existe."}, status=status.HTTP_400_BAD_REQUEST)

# Determina si un alumno ya firmó o no el compromiso de pago actual y devuelve la fecha de la firma
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
            firma_existe = FirmaCompromiso.objects.get(alumno=alumno, parametros_compromiso=parametros_compromiso)

            return Response({"firmado": firma_existe.fechaFirma}, status=status.HTTP_200_OK)
        
        except Alumno.DoesNotExist:
            return Response({"error": "El alumno no existe."}, status=status.HTTP_400_BAD_REQUEST)
        except ParametrosCompromiso.DoesNotExist:
            return Response({"error": "El compromiso de pago no existe."}, status=status.HTTP_400_BAD_REQUEST)

# Listar los alumnos que firmaron un compormiso de pago
class FirmaCompromisoActualListView(APIView):
    
    def get(self, request, *args, **kwargs):

        # Determinar el cuatrimestre en función del mes actual
        if 3 <= datetime.now().month <= 7:
            cuatrimestre = 1
        else:
            cuatrimestre = 2
        
        # Obtener el último compromiso de pago
        compromiso = ParametrosCompromiso.objects.filter(año=datetime.now().year, cuatrimestre=cuatrimestre).last()
        
        # Aca hacer el control de que esten inscriptos este cuatrimestre!
        alumnos = Alumno.objects.all().order_by('apellido')

        # Si no hay compromiso, se asume que nadie ha firmado y se envía `firmo_compromiso: false`
        if not compromiso:
            alumnos_con_firma = [
                {
                    'alumno': AlumnoSerializer(alumno).data,
                    'firmo_compromiso': False  # Nadie ha firmado si no hay compromiso
                }
                for alumno in alumnos
            ]
            return Response(alumnos_con_firma, status=status.HTTP_200_OK)

        
        # Obtener los firmantes del compromiso actual
        firmantes_ids = FirmaCompromiso.objects.filter(parametros_compromiso=compromiso).values_list('alumno_id', flat=True)
        
        # Crear una lista con los datos de los alumnos y si firmaron o no el compromiso
        alumnos_con_firma = []
        for alumno in alumnos:
            alumnos_con_firma.append({
                'alumno': AlumnoSerializer(alumno).data,
                'firmo_compromiso': alumno.id in firmantes_ids
            })

        return Response(alumnos_con_firma, status=status.HTTP_200_OK)


class EstadoDeCuentaAlumnoView(APIView):
    permission_classes = [IsAuthenticated] # IsAlumno

    def get(self, request):
        user = request.user  # Obtén el usuario autenticado

        if 3 <= datetime.now().month <= 7:
            cuatrimestre = 1
        else:
            cuatrimestre = 2

        try:
            alumno = Alumno.objects.get(user=user)  # Busca el alumno relacionado con el usuario autenticado
            compromiso = ParametrosCompromiso.objects.filter(año=datetime.now().year, cuatrimestre=cuatrimestre).last()
            queryset = Cuota.objects.filter(alumno=alumno, año=datetime.now().year)
            
            for cuota in queryset:
                cuota.aplicar_moras(compromiso)
            
            serializer = CuotaSerializer(queryset, many=True)
            return Response(serializer.data)

        except Alumno.DoesNotExist:
            return Response({"error": "El alumno no existe."}, status=status.HTTP_400_BAD_REQUEST)
        except ParametrosCompromiso.DoesNotExist:
            return Response({"error": "El compromiso de pago no existe."}, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request):
        # Obtén el ID del alumno desde el cuerpo de la solicitud
        alumno_id = request.data.get('alumno')

        if alumno_id is None:
            return Response({"error": "El ID del alumno no ha sido proporcionado."}, status=status.HTTP_400_BAD_REQUEST)

        if 3 <= datetime.now().month <= 7:
            cuatrimestre = 1
        else:
            cuatrimestre = 2

        try:
            alumno = Alumno.objects.get(id=alumno_id)  # Busca el alumno con el ID proporcionado
            compromiso = ParametrosCompromiso.objects.filter(año=datetime.now().year, cuatrimestre=cuatrimestre).last()
            queryset = Cuota.objects.filter(alumno=alumno, año=datetime.now().year)
            
            for cuota in queryset:
                cuota.aplicar_moras(compromiso)
            
            serializer = CuotaSerializer(queryset, many=True)
            return Response(serializer.data)

        except Alumno.DoesNotExist:
            return Response({"error": "El alumno no existe."}, status=status.HTTP_400_BAD_REQUEST)
        except ParametrosCompromiso.DoesNotExist:
            return Response({"error": "El compromiso de pago no existe."}, status=status.HTTP_400_BAD_REQUEST)

class ResumenAlumnoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if 3 <= datetime.now().month <= 7:
            cuatrimestre = 1
        else:
            cuatrimestre = 2

        try:
            alumno = Alumno.objects.get(user=user)
            compromiso = ParametrosCompromiso.objects.filter(año=datetime.now().year, cuatrimestre=cuatrimestre).last()
            
            saldo_vencido_resultado = saldo_vencido(alumno, compromiso)
            proximo_vencimiento_resultado = proximo_vencimiento(alumno)

            return Response({
                "saldoVencido": saldo_vencido_resultado,
                "proximaFechaVencimiento": proximo_vencimiento_resultado
            }, status=status.HTTP_200_OK)
        
        except Alumno.DoesNotExist:
            return Response({"error": "El alumno no existe."}, status=status.HTTP_400_BAD_REQUEST)
        except ParametrosCompromiso.DoesNotExist:
            return Response({"error": "El compromiso de pago no existe."}, status=status.HTTP_400_BAD_REQUEST)
        
class ObtenerMateriasPorCodigoView(APIView):
    def post(self, request):
        # 1. Obtener los códigos de materias desde el body de la request
        codigos = request.data.get('codigos', [])
        
        if not codigos or not isinstance(codigos, list):
            return Response(
                {"error": "Se debe proporcionar un array de códigos."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Filtrar las materias que coinciden con los códigos
        materias = Materia.objects.filter(codigo_materia__in=codigos)
        
        if not materias.exists():
            return Response(
                {"error": "No se encontraron materias con los códigos proporcionados."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # 3. Serializar y devolver los nombres de las materias
        serializer = MateriaSerializer(materias, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ObtenerPagoPorAlumnosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            alumno = Alumno.objects.get(user=user)
            pagos = Pago.objects.filter(alumno=alumno).order_by('-id')
            serializer = PagoSerializer(pagos, many=True)
            return Response(
            serializer.data
            , status=status.HTTP_200_OK)
        
        except Alumno.DoesNotExist:
            return Response({"error": "El alumno no existe."}, status=status.HTTP_400_BAD_REQUEST)
        except Pago.DoesNotExist:
            return Response({"error": "El pago no existe."}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):

        alumno_id = request.data.get('alumno')

        if alumno_id is None:
            return Response({"error": "El ID del alumno no ha sido proporcionado."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            alumno = Alumno.objects.get(id=alumno_id)  # Busca el alumno con el ID proporcionado
            pagos = Pago.objects.filter(alumno=alumno).order_by('-id')
            serializer = PagoSerializer(pagos, many=True)

            return Response(
            serializer.data
            , status=status.HTTP_200_OK)

        except Alumno.DoesNotExist:
            return Response({"error": "El alumno no existe."}, status=status.HTTP_400_BAD_REQUEST)
        except Pago.DoesNotExist:
            return Response({"error": "El pago no existe."}, status=status.HTTP_400_BAD_REQUEST)
        
#Importacion de las cuotas asociadas a los alumnos

class ImportarCuotaPIView(APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        
        if not file:
            return Response({"error": "No ha ingresado ningún archivo"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Determinar la extensión del archivo para elegir el método de lectura
            file_extension = file.name.split('.')[-1].lower()

            if file_extension == 'csv':
                df = pd.read_csv(file, header=1)
            elif file_extension in ['xlsx', 'xls']:
                
                df = pd.read_excel(file, engine='openpyxl', header=1)
            else:
                return Response({"error": "Tipo o formato de archivo no soportado, debe seleccionar csv o xlsx"}, status=status.HTTP_400_BAD_REQUEST)

            # Encontrar la primera fila con más de 10 columnas no nulas
            def has_more_than_n_columns(row, n=10):
                return row.notna().sum() > n

            header_row_index = df[df.apply(lambda row: has_more_than_n_columns(row), axis=1)].index.min()
            
            if pd.isna(header_row_index):
                return Response({"error": "No se encontró una fila adecuada para usar como encabezado."}, status=status.HTTP_400_BAD_REQUEST)

            # Establecer la fila identificada como encabezado y eliminar las filas anteriores
            df.columns = df.iloc[header_row_index]
            df = df[header_row_index + 1:].reset_index(drop=True)

            # Limpiar nombres de columnas y procesar
            df.columns = df.columns.str.strip()  # Limpiar espacios en los nombres de columnas
            df.columns = [str(col).lower() for col in df.columns]  # Convertir nombres a minúsculas
            
            
            # quito los tildes y los puntos, y reemplazar los espacios por guiones bajos
            df.columns = [unidecode(col).replace('.', '').replace(' ', '_') for col in df.columns]

            df['nombre_medio_de_pago'] = df['nombre_medio_de_pago'].astype(str)

            
            # Identifica los nombres de columna relevantes
            pagos=[]
            filas_ignoradas = []
            correctas = []
            errores=[]
            print(df.columns)
            index = header_row_index +3
            # Eliminar columnas duplicadas
            df = df.loc[:,~df.columns.duplicated()]
            for _, row in df.iterrows():
                
                index += 1
                print(index)
                if not has_more_than_n_columns(row, 10): # Verifica si la fila tiene al menos 10 columnas no nulas
                    filas_ignoradas.append({
                        "error": f"fila {index}: no tiene suficientes columnas con datos para procesar(falta legajo, nombre y apellido), por lo que se ha ignorado."
                    })
                    continue
                
                #verificar que el numero de recibo sea un numero
                try:
                    numero = int(row['nro_recibo'])
                except ValueError:
                    errores.append({
                        "error": f"fila {index}: El número de recibo no es un número válido."
                    })
                    continue
                if buscarReciboRepetido(numero,errores,index) == True:
                    continue
                
                data = row.to_dict()
                medio_pago = data.get('nombre_medio_de_pago')
                #en este caso debo preguntar si el nombre y apellido vienen juntos, y si es asi, tomarlo. como condicion
                if ',' in data.get('nombre_originante_del_ingreso'):
                    nombre= data.get('nombre_originante_del_ingreso').split(',')[0]
                    apellido= data.get('nombre_originante_del_ingreso').split(',')[1]
                else:
                    errores.append({
                        "error": f"fila {index}: El nombre y apellido no están separados por coma."
                    })
                    continue
                    

                #en este caso debo preguntar si la descripcion de la cuota tiene el mes, y si es asi, tomarlo. como condicion
                descripcion_cuota = data.get('descripcion_recibo')
                
                #en el dni debo controlar que sea un numero valido, en caso de ser 0. debo tratar por su nombe y apellido
                dni = data.get('nro_doc')
                
                #EN CASO DE QUE SEA NEGATIVO, que hago con su  carga? sumo el total?
                monto= data.get('monto')
                
                #necesito saber como viene la fecha, y como es el formato
                fecha_pago = data.get('fecha_dga')
                
                numeroRecibo = data.get('nro_recibo')
                
                
                #tratamiendo del pago
                
                medio_pago= tratamientoMedioPago(medio_pago)
                    
                #tratamiento de los meses
                                
                #el tratamiento de los alumnos y los pagos mas complejo
                try:
                    correcto= tramientoAlumno(nombre, apellido, dni, monto, medio_pago,errores,index,numeroRecibo)
                    print(correcto)
                    if correcto=="correcto":
                        correctas.append({
                            "nombre": nombre,
                            "apellido": apellido,
                            "numero_recibo": numeroRecibo,
                            "monto": monto,
                            "medio_pago": medio_pago,
                        })
                except Exception as e:
                    errores.append({
                        "error": f"fila {index}: {str(e)}"
                    })
                
            return Response({
                "message": "Importación de pagos completada",
                "pagos": correctas,
                "errores": errores,
             
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

def buscarReciboRepetido(numeroRecibo,errores,index):
    if Pago.objects.filter(numero_recibo=numeroRecibo).exists():
        errores.append({
            "error": f"fila {index}: El número de recibo {numeroRecibo} ya ha sido registrado."
        })
        return True
    return False

  
def tramientoAlumno(nombre, apellido, dni, monto, medio_pago, errores,index,numeroRecibo):
    try:
        alumno = buscar_alumno_por_dni_o_nombre(dni, nombre, apellido)
        if not alumno:
            print("no existe")
            errores.append({
                "error": f"fila {index}: El alumno con DNI {dni} o nombre {nombre} {apellido} no existe."
            })
            
        tratamientoCoutaCero(alumno.id, monto, medio_pago,numeroRecibo)
        return "correcto"
    except Exception as e:
        return str(e)




def tratamientoPago(id_alumno, monto,medio_pago,numeroRecibo):
    # crear un pago
    
    # TENER CUIDADO CON LA FECHA PORQUE ES LA DEL PAGO QUE SE CONFIRMO EN SYSADMIN, PARA LA PRUEBA HARÉ UNA FECHA DE HOY porque no me queda en claro como recibe la fecha
    #que diferencia hay entre monto_informado y monto_confirmado?
    pago = Pago(
        alumno_id=id_alumno,
        monto_confirmado=monto,
        numero_recibo=numeroRecibo,
        fecha_pago_confirmado=datetime.now(),
        forma_pago=medio_pago,
        comprobante_de_pago=None,
    )
     # Guardar el pago en la base de datos
    pago.save()

    # Obtener las cuotas del alumno que aún no han sido completamente pagadas
    cuotas_pendientes = Cuota.objects.filter(alumno_id=id_alumno, importePagado__lt=F('total'))

    # El monto restante es la cantidad del pago recibido
    monto_restante = Decimal(monto)

    for cuota in cuotas_pendientes:
        # Calcular cuánto falta para pagar la cuota completamente
        monto_a_pagar = cuota.total - cuota.importePagado

        if monto_restante <= 0:
            break  # No queda más dinero para pagar

        # Si el monto restante es mayor o igual a lo que falta en la cuota
        if monto_restante >= monto_a_pagar:
            # Pagar la cuota completamente
            cuota.importePagado += monto_a_pagar
            monto_pagado = monto_a_pagar
        else:
            # Pagar solo parte de la cuota
            cuota.importePagado += monto_restante
            monto_pagado = monto_restante

        # Crear el registro en la tabla intermedia PagoCuota
        DetallePago.objects.create(
            pago=pago,
            cuota=cuota,
            monto_cuota=monto_pagado
        )
        # Restar el monto pagado de la cantidad restante
        monto_restante -= monto_pagado
    
def tratamientoCoutaDistintoCero(id_alumno, monto, medio_pago):
    cuota = Cuota.objects.get(alumno_id=id_alumno, nroCuota=cuota)
    cuota.importePagado +=monto
    cuota.save()
    tratamientoPago(id_alumno, monto,medio_pago)
    
    
    
def tratamientoCoutaCero(id_alumno, monto, medio_pago,numeroRecibo):
   # Filtra las cuotas pendientes para el alumno
    cuotas_pendientes = Cuota.objects.filter(
        total__gt=F('importePagado'), alumno_id=id_alumno  # total mayor que el importe pagado
    ).order_by('fechaPrimerVencimiento')
    monto_original=monto
    tratamientoPago(id_alumno, monto_original, medio_pago,numeroRecibo)
    # Itera sobre las cuotas mientras haya monto por pagar
    while monto > 0 and cuotas_pendientes.exists():
        # Obtén la cuota más reciente
        cuota_mas_reciente = cuotas_pendientes.first()

        # Calcula el importe pendiente de la cuota
        importe_pendiente = cuota_mas_reciente.total - cuota_mas_reciente.importePagado

        # Aplica el pago a la cuota
        if monto >= importe_pendiente:
            # Si el monto es mayor o igual al importe pendiente
            monto -= importe_pendiente
            cuota_mas_reciente.importePagado = cuota_mas_reciente.total

            cuota_mas_reciente.estado = 'Pagada'
        else:
            # Si el monto es menor que el importe pendiente
            cuota_mas_reciente.importePagado += monto
            monto = 0  # El monto se ha agotado

            if cuota_mas_reciente.fechaPrimerVencimiento < now().date():
                cuota_mas_reciente.estado = "Vencida"
            else:
                cuota_mas_reciente.estado = "Pendiente"
                
        cuota_mas_reciente.importeInformado = cuota_mas_reciente.importePagado

        # Guarda la cuota actualizada
        cuota_mas_reciente.save()

        # Actualiza el queryset para obtener la siguiente cuota pendiente
        cuotas_pendientes = Cuota.objects.filter(
            total__gt=F('importePagado'), alumno_id=id_alumno
        ).order_by('fechaPrimerVencimiento')
        
            # Verifica si el alumno está al día con la cuota del mes anterior
        hoy = timezone.now().date()
        diez_dias_margen = hoy - timedelta(days=10)

            # Lógica para manejar el mes anterior (considerando el cambio de año)
        if hoy.month == 1:
            mes_anterior = 12
            ano_anterior = hoy.year - 1
        else:
            mes_anterior = hoy.month - 1
            ano_anterior = hoy.year

        # Verifica si hay cuotas pendientes del mes anterior
        cuota_mes_anterior = Cuota.objects.filter(
            alumno_id=id_alumno,
            fechaPrimerVencimiento__month=mes_anterior,
            fechaPrimerVencimiento__year=ano_anterior,
            total__gt=F('importePagado')  # Cuota no está completamente pagada
        ).exists()

        # Verifica si hay cuotas pendientes del mes en curso y dentro del margen de 10 días
        cuota_mes_actual_vencida = Cuota.objects.filter(
            alumno_id=id_alumno,
            fechaPrimerVencimiento__lte=diez_dias_margen,  # Fecha de vencimiento pasó el margen
            total__gt=F('importePagado')  # Cuota no está completamente pagada
        ).exists()

        # Actualiza el estado del alumno si no tiene cuotas pendientes del mes anterior
        # y está dentro del margen de 10 días del mes actual
        if not cuota_mes_anterior and not cuota_mes_actual_vencida:
            alumno = Alumno.objects.get(id=id_alumno)
            alumno.pago_al_dia = True
            alumno.save()
  
    
                            
                            


def tratamientoMedioPago(medio_pago):
    diferentes_pagos={
                    "caja": "efectivo",
                    "transferencia": "transferencia",
                }
    for palabra,valor in diferentes_pagos.items():
        if palabra in medio_pago.lower():
            medio_pago = valor
    
    if medio_pago not in ["efectivo", "transferencia"]:
        medio_pago = "otro"
    return medio_pago

            
            


def buscar_alumno_por_dni_o_nombre(dni, nombre, apellido):
    if dni != 0:
        alumno= Alumno.objects.filter(dni=dni).first()
        if alumno:
            return alumno
        else:
            return None
        
    else:
        nombre_apellido = nombre.lower().split() + apellido.lower().split()
        filtro = Q()
        for nombre in nombre_apellido:
            filtro &= (Q(nombre__icontains=nombre) | Q(apellido__icontains=nombre))
        return Alumno.objects.filter(filtro).first()
    
    
# Obtener un alumno por su id
class AlumnoDetailView(generics.RetrieveAPIView):
    serializer_class = AlumnoSerializer

    def get(self, request):
        try:
            # Obtener el perfil del alumno autenticado
            alumno = Alumno.objects.get(user=request.user)
            serializer = AlumnoSerializer(alumno)
            return Response(serializer.data)
        except Alumno.DoesNotExist:
            # Si el alumno no existe, devolver un error personalizado
            return Response(
                {"error": "Alumno no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
            
class PagoView(APIView):

    def post(self, request, *args, **kwargs):
        alumno = Alumno.objects.get(user=request.user)

        # Crear una notificación
        notificacion = Notificacion.objects.create(
            alumno=alumno,
            mensaje=f'Se ha pagado correctamente la cuota...',
            fecha=timezone.now()
        )

        # Enviar notificación a través de WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notificaciones_{alumno.id}',  # Asegúrate de que cada alumno tenga un grupo único
            {
                'type': 'send_notification',
                'message': {
                    'mensaje': notificacion.mensaje,
                    'fecha': notificacion.fecha.strftime('%Y-%m-%d %H:%M:%S')
                }
            }
        )

        return Response({'status': 'Pago procesado y notificación enviada'})
    
    
class MensajesView(APIView):
    def get(self, request):
        # Obtener todos los mensajes o filtrar según el usuario autenticado
        mensajes = Notificacion.objects.all()  # O usa un filtro por usuario
        serializer = NotificacionSerializer(mensajes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
#Filtrar alumno que no pagaron, eso te hace preguntando si la fecha de vencimiento es menor al dia 10 del mes siguiente

class AlumnosNoPagaronView(APIView):
    def get(self, request):
        # Obtener los alumnos que no pagaron y que la fecha de vencimiento sea menor al día 10 del mes siguiente y si pago al dia esta en false
        
        
        
        alumnos = Alumno.objects.filter(cuota__fechaPrimerVencimiento__lt=datetime.now().replace(day=10))
        alumnos = alumnos.filter(pago_al_dia=True)
        serializer = AlumnoSerializer(alumnos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CambiarEstadoPagoAPIView(APIView):

    def patch(self, request, id):
        try:
            alumno = Alumno.objects.get(id=id)
        except Alumno.DoesNotExist:
            return Response({'error': 'Alumno no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        # Actualizamos el estado de 'pago_al_dia'
        pago_al_dia = request.data.get('pago_al_dia', None)
        if pago_al_dia is None:
            return Response({'error': 'El campo "pago_al_dia" es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)

        alumno.pago_al_dia = pago_al_dia
        alumno.save()

        return Response({'message': 'El estado de pago ha sido actualizado correctamente'}, status=status.HTTP_200_OK)
    
    

class AlumnosCompromisoFirmadoView(APIView):
    def get(self, request):
        # Obtener el compromiso del año actual
        compromiso_actual = ParametrosCompromiso.objects.filter(año=datetime.now().year).last()

        # Contar alumnos que no están al día y han firmado el compromiso actual
        total_alumnos = Alumno.objects.filter(
            pago_al_dia=False,
            firmacompromiso__parametros_compromiso=compromiso_actual
        ).count()

        return Response( total_alumnos, status=status.HTTP_200_OK)
    

class AlumnosNoPagaron2View(APIView):
    def get(self, request):
        # Fecha actual
        hoy = datetime.now()
        dia_tolerancia = 10
        fecha_limite_mes_actual = hoy.replace(day=dia_tolerancia)

        # Alumnos que deben la cuota de este mes y aún están dentro del periodo de tolerancia
        alumnos_que_deben_este_mes = Alumno.objects.filter(
            cuota__fechaPrimerVencimiento__month=hoy.month,  # Cuotas de este mes
            cuota__total__gt=F('cuota__importePagado'),  # Cuota no está completamente pagada
            pago_al_dia=True  # Estaban al día antes de este mes
        ).distinct()

        # Alumnos que deben cuotas de meses anteriores
        alumnos_con_cuotas_vencidas = Alumno.objects.filter(
            cuota__estado="Vencida",  # Cuotas anteriores
            # pago_al_dia=False  # No están al día
        ).distinct()

        # Alumnos inhabilitados (pago_al_dia=False)
        alumnos_inhabilitados = Alumno.objects.filter(
            pago_al_dia=False
        ).distinct()

        # Unir todos los conjuntos de alumnos
        alumnos = alumnos_con_cuotas_vencidas | alumnos_inhabilitados

        # Serializar la lista de alumnos con sus cuotas vencidas
        serializer = AlumnosCoutasNoPagadas(alumnos, many=True)

        # Devolver la lista de alumnos con la información solicitada
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class InformarPagoCuotas(APIView):
    permission_classes = [IsAuthenticated] # IsAlumno

    def post(self, request):
        user = request.user  # Obtén el usuario autenticado

        try:
            alumno = Alumno.objects.get(user=user)
            
            # Obtén las cuotas seleccionadas desde el cuerpo de la solicitud
            cuotas_seleccionadas = request.data.get('cuotasSeleccionadas', [])

            # Filtra las cuotas por el alumno y el año actual
            queryset = Cuota.objects.filter(alumno=alumno, año=datetime.now().year, nroCuota__in=cuotas_seleccionadas)
            
            monto_restante = Decimal(request.data.get("montoAPagar"))
            for cuota in queryset:
                # Calcular cuánto falta para pagar la cuota completamente
                monto_a_pagar = cuota.total - cuota.importeInformado

                if monto_restante <= 0:
                    break  # No queda más dinero para informar

                # Si el monto restante es mayor o igual a lo que falta en la cuota
                if monto_restante >= monto_a_pagar:
                    # Informar la cuota completamente
                    cuota.importeInformado += monto_a_pagar
                    monto_pagado = monto_a_pagar
                else:
                    # Pagar solo parte de la cuota
                    cuota.importeInformado += monto_restante
                    monto_pagado = monto_restante

                cuota.save()
                # Restar el monto pagado de la cantidad restante
                monto_restante -= monto_pagado
            
            serializer = CuotaSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Alumno.DoesNotExist:
            return Response({"error": "El alumno no existe."}, status=status.HTTP_400_BAD_REQUEST)
        except Cuota.DoesNotExist:
            return Response({"error": "La cuota no existe.."}, status=status.HTTP_400_BAD_REQUEST)


class AlumnosCuotasVencidas(APIView):
    def get(self, request):
        # Fecha actual
        hoy = datetime.now()
        dia_tolerancia = 10
        fecha_limite_mes_actual = hoy.replace(day=dia_tolerancia)

        # Obtener alumnos que:
        # 1. Deben la cuota de este mes pero están dentro del periodo de tolerancia
        # 2. O tienen cuotas vencidas de meses anteriores
        # 3. O están inhabilitados (pago_al_dia=False)
        
        # Alumnos que deben la cuota de este mes y aún están dentro del periodo de tolerancia
        alumnos_que_deben_este_mes = Alumno.objects.filter(
            cuota__fechaPrimerVencimiento__month=hoy.month,  # Cuotas de este mes
            cuota__total__gt=F('cuota__importePagado'),  # Cuota no está completamente pagada
            pago_al_dia=True  # Estaban al día antes de este mes
        ).distinct()

        # Alumnos que deben cuotas de meses anteriores
        alumnos_con_cuotas_vencidas = Alumno.objects.filter(
            cuota__fechaPrimerVencimiento__lt=hoy.replace(day=1),  # Cuotas anteriores
            pago_al_dia=False  # No están al día
        ).distinct()

        # Alumnos inhabilitados (pago_al_dia=False)
        alumnos_inhabilitados = Alumno.objects.filter(
            pago_al_dia=False
        ).distinct()

        # Unir todos los conjuntos de alumnos
        alumnos = alumnos_que_deben_este_mes | alumnos_con_cuotas_vencidas | alumnos_inhabilitados

        # Obtener la lista de cuotas vencidas por alumno
        alumnos_con_cuotas = []
        for alumno in alumnos:
            cuotas_vencidas = alumno.cuota_set.filter(
                total__gt=F('importePagado'),  # Cuotas no pagadas completamente
                fechaPrimerVencimiento__lt=hoy  # Cuotas cuyo vencimiento fue en el pasado
            ).values('id', 'importe', 'importePagado', 'fechaPrimerVencimiento')
            
            alumnos_con_cuotas.append({
                'alumno_id': alumno.id,
                'nombre': alumno.nombre,
                'apellido': alumno.apellido,
                'cuotas_vencidas': list(cuotas_vencidas)
            })

        # Devolver la lista de alumnos con cuotas vencidas
        return Response(alumnos_con_cuotas, status=status.HTTP_200_OK)

class SolicitarProrrogaView(APIView):
    permission_classes = [IsAuthenticated]  # Solo usuarios autenticados

    def post(self, request):
        user = request.user  # Obtener el usuario autenticado
        codigo_materia = request.data.get('materia')  # Obtener el ID de la materia desde el request
        analitico = request.FILES.get('analitico')  # Obtener el archivo del analítico
        motivo = request.data.get('motivo', '')  # Obtener el motivo (opcional)

        try:
            # Obtener el alumno asociado al usuario autenticado
            alumno = Alumno.objects.get(user=user)
            # Obtener la materia seleccionada
            materia = Materia.objects.get(codigo_materia=codigo_materia)

            # Verificar si ya existe una solicitud para la misma materia
            if SolicitudProrroga.objects.filter(alumno=alumno, materia=materia).exists():
                return Response(
                    {"error": "Ya has solicitado una prórroga para esta materia."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Crear y guardar la solicitud de prórroga
            solicitud = SolicitudProrroga(
                alumno=alumno,
                materia=materia,
                analitico=analitico,
                motivo=motivo,
            )
            solicitud.save()

            return Response(
                {"message": "Prórroga solicitada exitosamente."},
                status=status.HTTP_201_CREATED,
            )

        except Alumno.DoesNotExist:
            return Response(
                {"error": "El alumno no existe."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Materia.DoesNotExist:
            return Response(
                {"error": "La materia no existe."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except IntegrityError:
            return Response(
                {"error": "Error al procesar la solicitud."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
class ProrrogasPorAlumnoView(APIView):
    permission_classes = [IsAuthenticated]  # Solo usuarios autenticados

    def get(self, request, *args, **kwargs):
        user = request.user
        print(user)
        try:
            alumno = Alumno.objects.get(user=user)
            queryset = SolicitudProrroga.objects.filter(alumno=alumno)
            serializer = SolicitudProrrogaSerializer(queryset, many=True)
            if queryset:
                return Response(serializer.data)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        
        except Alumno.DoesNotExist:
            return Response(
                {"error": "El alumno no existe."},
                status=status.HTTP_400_BAD_REQUEST,
            )