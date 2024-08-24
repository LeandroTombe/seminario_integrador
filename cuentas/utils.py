from datetime import datetime
import os
import random
from django.core.mail import EmailMessage
from django.core.mail import send_mail
import pandas as pd
from estudiantes.models import Alumno


import threading


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        EmailThread(email).start()


    def  email_otp_verifcation(self,email):
            subject='Codigo de verificacion para cambiar la contraseña'
            otp=random.randint(1,100)
            message=f'su codigo es: {otp}'
            email_from='tup@gmail.com'
            send_mail(subject,message,email_from,[email])
            user_obj=Alumno.objects.get(email=email).user
            #obtener el objeto del usuario
            user_obj.otp=otp
            user_obj.save()
        
    def  password_reset_otp(email):
            subject='Codigo de verificacion para cambiar la contraseña'
            otp=random.randint(100000,999999)
            message=f'su codigo es: {otp}'
            email_from='tup@gmail.com'
            send_mail(subject,message,email_from,[email])
            user_obj=Alumno.objects.get(email=email).user
            user_obj.otp=otp
            user_obj.save()


def exportar_correctas(tablas_correctas):
    # Crear una carpeta con la fecha y hora actual
    fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    export_dir = f'exportaciones/{fecha_hora}'
    os.makedirs(export_dir, exist_ok=True)

    # Crear DataFrame para filas correctas
    if tablas_correctas:
        df_correctas = pd.DataFrame(tablas_correctas)
        print(f"Columnas disponibles en tablas_correctas:\n{df_correctas.columns.tolist()}")
        # Seleccionar solo las columnas requeridas si están presentes
        columnas_correctas = ["legajo", "nombre", "apellido"]
        columnas_presentes = [col for col in columnas_correctas if col in df_correctas.columns]
        df_correctas = df_correctas[columnas_presentes]
        correctas_file_path = os.path.join(export_dir, 'filas_correctas.xlsx')
        df_correctas.to_excel(correctas_file_path, index=False, engine='openpyxl')
        print(f'Archivo de filas correctas guardado en: {correctas_file_path}')
    else:
        print("No hay datos para exportar en filas correctas.")

   


def exportar_incorrectas(tablas_errores):
    # Crear una carpeta con la fecha y hora actual
    fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    export_dir = f'exportaciones/{fecha_hora}'
    os.makedirs(export_dir, exist_ok=True)
     # Crear DataFrame para filas incorrectas
    if tablas_errores:
        df_errores = pd.DataFrame(tablas_errores)
        print(f"Columnas disponibles en tablas_errores:\n{df_errores.columns.tolist()}")
        # Seleccionar solo las columnas requeridas si están presentes
        columnas_errores = ["legajo", "nombre", "apellido"]
        columnas_presentes = [col for col in columnas_errores if col in df_errores.columns]
        df_errores = df_errores[columnas_presentes]
        errores_file_path = os.path.join(export_dir, 'filas_incorrectas.xlsx')
        df_errores.to_excel(errores_file_path, index=False, engine='openpyxl')
        print(f'Archivo de filas incorrectas guardado en: {errores_file_path}')
    else:
        print("No hay datos para exportar en filas incorrectas.")