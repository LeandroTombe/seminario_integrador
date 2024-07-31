import mysql.connector
import environ

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