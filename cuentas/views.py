from django.conf import settings
import numpy as np
from rest_framework.response import Response
from rest_framework import status,views,generics
from rest_framework.views import APIView
from .models import User
from .resources import UserResource
from django.http import HttpResponse
from .serializers import ResendOtpSerializer, UserPasswordResetUpdateserializer, UserRegisterSerializer,UserPasswordResetSerailizer,LogoutSerializer, UserVerifyEmailSerializer
from .utils import Util, exportar_correctas, exportar_incorrectas
from django.contrib.auth.password_validation  import validate_password
from .permissions import IsAlumno
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from .serializers import CustomToken


import pandas as pd
from estudiantes.models import Alumno, Materia
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from unidecode import unidecode



#Registro de usuario

class UserRegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "Usuario creado exitosamente."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

#Login de usuario
    
class UserLoginView(APIView):
    def post(self, request, *args, **kwargs):
        legajo = request.data.get('legajo')
        password = request.data.get('password')
        try:
            user = User.objects.get(legajo=legajo)
        except User.DoesNotExist:
            return Response({"message": "legajo inexistente"}, status=status.HTTP_404_NOT_FOUND)
        if not user.check_password(password):
            return Response({"message": "Contraseña incorrecta."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generar un token JWT en lugar de usar Token
        refresh = CustomToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)


User = get_user_model()

"""
         - **actualizadas** (list): Una lista de diccionarios con los registros de alumnos que se han actualizado. Cada diccionario incluye un mensaje con la información sobre la actualización.
        - **cantidad_filas_actualizadas** (int): La cantidad total de filas de alumnos que se han actualizado.
        - **errores** (list): Una lista de diccionarios con los errores encontrados durante el procesamiento del archivo. Cada diccionario contiene un mensaje de error.
        - **correctas** (list): Una lista de diccionarios con los registros de alumnos que se han creado correctamente. Cada diccionario incluye los datos del alumno (legajo, nombre, apellido).
        - **cantidad_errores** (int): La cantidad total de errores encontrados durante el procesamiento del archivo.
        - **cantidad_filas_correctas** (int): La cantidad total de filas de datos de alumnos que se han procesado correctamente y creado en la base de datos.
"""

def crear_actualizar_usuario(legajo, nombre, apellido):
    # Intenta obtener el usuario existente
    user = User.objects.filter(legajo=legajo).first()
    
    if user:
        # Si el usuario existe, solo actualiza los campos de nombre y apellido
        user.nombre = nombre
        user.apellido = apellido
        user.save()
    else:
        # Si el usuario no existe, crea uno nuevo
        user = User.objects.create_user(
            legajo=legajo,
            nombre=nombre,
            apellido=apellido,
            password=str(legajo),  # Encriptar la contraseña usando el legajo como password
            group='alumno'
        )
        # Asignar el grupo 'alumno'
        group, created = Group.objects.get_or_create(name='alumno')
        user.groups.add(group)
    
    return user
def crear_actualizar_alumno(user, nombre, apellido, legajo,dni,email):
    creado = False
    actualizado = False

    if Alumno.objects.filter(legajo=legajo).exists():
        alumno = Alumno.objects.get(legajo=legajo)

        # Verificar si los campos necesitan ser actualizados
        if alumno.nombre != nombre or alumno.apellido != apellido or alumno.dni != dni:
            alumno.nombre = nombre
            alumno.apellido = apellido
            alumno.dni = dni
            alumno.user = user
            alumno.save()
            actualizado = True
    else:
        Alumno.objects.create(
            legajo=legajo,
            nombre=nombre,
            apellido=apellido,
            dni=dni,
            email=email,
            user=user
        )
        creado = True

    return creado, actualizado

def agregar_materias(legajo,codigoMateria):
    # Obtener el alumno por legajo
    
    alumno = Alumno.objects.get(legajo=legajo)
    materia = Materia.objects.get(idMateria=codigoMateria)
    
    alumno.materias.add(materia)
    
    
    


class ImportarAlumnoAPIView(views.APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        
        if not file:
            return Response({"error": "No ha ingresado ningún archivo"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Determinar la extensión del archivo para elegir el método de lectura
            file_extension = file.name.split('.')[-1].lower()

            if file_extension == 'csv':
                df = pd.read_csv(file, header=None)
            elif file_extension in ['xlsx', 'xls']:
                df = pd.read_excel(file, engine='openpyxl', header=None)
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
            
            
            if 'apellido y nombres' in df.columns:
                # Separar el campo 'apellido y nombres' en 'apellido' y 'nombre'
                df[['apellido', 'nombre']] = df['apellido y nombres'].str.split(',', expand=True)
                df.drop(columns=['apellido y nombres'], inplace=True)
            
            
            # quitar los tildes y los puntos, y reemplazar los espacios por guiones bajos
            df.columns = [unidecode(col).replace('.', '').replace(' ', '_') for col in df.columns]
            print(df.columns)
            # Identifica los nombres de columna relevantes
            legajo_col = next((col for col in df.columns if 'legajo' in col), None)

            if not all([legajo_col]):
                return Response({"error": "No se encontraron las columnas requeridas en el archivo."}, status=status.HTTP_400_BAD_REQUEST)

            tabla_actualizada = []
            tabla_errores = []
            tabla_correctas = []
            filas_errores = []
            filas_ignoradas = []
            index = header_row_index +1
            total_general = 0
            
            for _, row in df.iterrows():
                index += 1
                if not has_more_than_n_columns(row, 10): # Verifica si la fila tiene al menos 10 columnas no nulas
                    filas_ignoradas.append({
                        "error": f"fila {index}: no tiene suficientes columnas con datos para procesar, por lo que se ha ignorado."
                    })
                    continue
                
                data = row.to_dict()
                legajo = data.get(legajo_col)
                nombre = data.get('nombre')
                apellido = data.get('apellido')
                dni = data.get('documento')
                email = data.get('mail')
                materia=data.get('materia')

                
                total_general += 1
                # Verificar si los valores son válidos
                if pd.isna(legajo) or pd.isna(nombre):
                    filas_errores.append({
                        "error": f"fila {index}: le falta el legajo, el nombre o el apellido."
                    })
                    
                else:
                    # Crear o actualizar el registro de user
                    user=crear_actualizar_usuario(legajo,nombre,apellido)

                    # Crear o actualizar el registro de alumno
                    creado,actualizado= crear_actualizar_alumno(user,nombre,apellido,legajo,dni,email)
                    agregar_materias(legajo,materia)
                    if creado:
                        tabla_correctas.append({
                            "legajo": legajo,
                            "nombre": nombre,
                            "apellido": apellido,
                            "dni": dni,
                            "email": email,
                        })
                    elif actualizado:
                        tabla_actualizada.append({
                           "mensaje": f"fila {index}: el legajo {legajo} se ha actualizado el nombre a {nombre} y apellido a {apellido} ."
                        })

            exportar_correctas(tabla_correctas)
            exportar_incorrectas(tabla_errores)
            
            cantidad_errores = len(filas_errores)
            cantidad_filas_correctas = len(tabla_correctas)
            cantidad_filas_actualizadas = len(tabla_actualizada)
            cantidad_filas_ignoradas = len(filas_ignoradas)
            total_procesadas=cantidad_filas_correctas + cantidad_filas_actualizadas  + cantidad_errores
            return Response({
                "actualizadas": tabla_actualizada,
                "cantidad_filas_actualizadas": cantidad_filas_actualizadas,
                "errores": filas_errores,
                "correctas": tabla_correctas,
                "cantidad_errores": cantidad_errores,
                "cantidad_filas_correctas": cantidad_filas_correctas,
                "filas_ignoradas": filas_ignoradas,
                "cantidad_filas_ignoradas": cantidad_filas_ignoradas,
                "total_procesadas": total_procesadas,
                "total": total_general
                
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        


"""
def exportar_correctas(tabla_correctas):
    fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    export_dir = f'media/exportaciones/{fecha_hora}'
    os.makedirs(export_dir, exist_ok=True)

    df_correctas = pd.DataFrame(tabla_correctas)
    columnas_correctas = ["legajo", "nombre", "apellido"]
    columnas_presentes = [col for col in columnas_correctas if col in df_correctas.columns]
    df_correctas = df_correctas[columnas_presentes]

    correctas_file_path = os.path.join(export_dir, 'filas_correctas.xlsx')
    df_correctas.to_excel(correctas_file_path, index=False, engine='openpyxl')

    return f'/media/exportaciones/{fecha_hora}/filas_correctas.xlsx'

def exportar_incorrectas(tabla_errores):
    fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    export_dir = f'media/exportaciones/{fecha_hora}'
    os.makedirs(export_dir, exist_ok=True)

    df_errores = pd.DataFrame(tabla_errores)
    columnas_errores = ["legajo", "nombre", "apellido"]
    columnas_presentes = [col for col in columnas_errores if col in df_errores.columns]
    df_errores = df_errores[columnas_presentes]

    errores_file_path = os.path.join(export_dir, 'filas_incorrectas.xlsx')
    df_errores.to_excel(errores_file_path, index=False, engine='openpyxl')

    return f'/media/exportaciones/{fecha_hora}/filas_incorrectas.xlsx'
"""
        
class ExportarUsuariosAPIView(views.APIView):
    #permission_classes = [CanExportData]

    def get(self, request, *args, **kwargs):
        user_resource = UserResource()
        dataset = user_resource.export()
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="usuarios.csv"'
        return response
    
#reseteo de password

class UserPasswordResetView(APIView):
    def post(self,request,fromat=None):
        serializer=UserPasswordResetSerailizer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email=serializer.validated_data['email']
            user=User.objects.filter(email=email).first()
            if user:
                Util.password_reset_otp(user.email)
                return Response({'msg':'Codigo para el reseteo de password enviado correctamente, por favor verifique su email'},status=status.HTTP_200_OK)
            return Response({'msg':'user is not exits'},status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.error,status=status.HTTP_400_BAD_REQUEST) 
    
    
class UserPasswordResetUpdateView(APIView):
    def post(self,request):
        serializer=UserPasswordResetUpdateserializer(data=request.data)
        print(serializer)
        if serializer.is_valid(raise_exception=True):
            password=serializer.validated_data['password']
            password2=serializer.validated_data['password2']
            otp=serializer.validated_data['otp']
            user=User.objects.filter(otp=otp).first()
            if not user:
                 return Response({"msg":"La cuenta no existe"},status=status.HTTP_404_NOT_FOUND)
            try:
                 validate_password(password=password)
                 if password!=password2:
                            return Response({'msg':'los password escritos no coinciden'},status=status.HTTP_404_NOT_FOUND)
            except ValidationError as err:
                 return Response(ValidationError({'password':err.messages})) 
            if user.otp!=otp:
                    return Response({'msg':'has ingresado un codigo incorrecto'},status=status.HTTP_404_NOT_FOUND)
            user.set_password(password)
            user.save()
            return Response({'msg':'el password se ha modificado correctamente'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class UserVerifyEmailView(APIView):
    def post(self, request):
        serializer = UserVerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            user = User.objects.filter(email=email).first()
            if not user:
                return Response({
                    'data': 'la cuenta con el email ingresado no existe'
                }, status=status.HTTP_400_BAD_REQUEST)
            if user.otp != otp:
                return Response({
                    'data': 'codigo incorrecto'
                }, status=status.HTTP_400_BAD_REQUEST)
            user.is_verified = True
            user.save()
            return Response({
                'msg': 'email verificado correctamente'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResendOtpView(APIView):
    def post(self, request):
        serializer = ResendOtpSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            if user :
                if not user.is_verified:   
                        Util.email_otp_verifcation(user.email)
                        return Response({'msg': 'codigo re enviado, por favor verifique en su email'}, status=status.HTTP_200_OK)
                else:
                        return Response({'msg': 'Email ya ha sidi verificado'}, status=status.HTTP_200_OK)
            else:
                 return Response({'msg': 'la cuenta con el email ingresado no existe'}, status=status.HTTP_404_NOT_FOUND) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


#testing para probar el permiso
class TestView(APIView):
    permission_classes = [IsAuthenticated, IsAlumno]

    def get(self, request, *args, **kwargs):
        return Response({"message": "Acceso concedido"}, status=status.HTTP_200_OK)
    


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer




    
    """
                # Buscar registros existentes por email o legajo
                legajo = data.get('legajo')
                existing_alumno_by_legajo = Alumno.objects.filter(legajo=legajo).first()
                existing_alumno_by_email = Alumno.objects.filter(user=user).first()

                if existing_alumno_by_legajo:
                    # Actualizar por legajo
                    instance = existing_alumno_by_legajo
                    serializer = AlumnoSerializer(instance, data=data, partial=True)
                elif existing_alumno_by_email:
                    # Actualizar por email
                    instance = existing_alumno_by_email
                    serializer = AlumnoSerializer(instance, data=data, partial=True)
                else:
                    # Crear nuevo registro
                    serializer = AlumnoSerializer(data=data)
                
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    """