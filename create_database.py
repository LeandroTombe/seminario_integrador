import os
import mysql.connector
import environ

# Configura el entorno de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tup.settings")  # Cambia "myproject" por el nombre de tu proyecto
import django


django.setup()

# Lee el archivo .env
env = environ.Env()
environ.Env.read_env()

def create_database():
    conn = mysql.connector.connect(
        host=env('DB_HOST'),
        user=env('DB_USER'),
        password=env('DB_PASSWORD')
    )
    cursor = conn.cursor()

    database_name = env('DB_NAME')

    # Crear la base de datos si no existe
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
    print(f"Base de datos '{database_name}' creada exitosamente")

    cursor.close()
    conn.close()

if __name__ == '__main__':
    create_database()