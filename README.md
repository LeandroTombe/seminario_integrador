# Proyecto Django

Este proyecto utiliza Django junto con varios paquetes para proporcionar una funcionalidad completa.

## Pasos para configurar el proyecto

# Crear y activar el entorno virtual
python -m venv env

source env/bin/activate 
En Windows usa  `env\Scripts\activate`

# Instalar dependencias
pip install -r requirements.txt

# Crear la base de datos
python create_database.py

# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario (esto te pedirá que ingreses los detalles del superusuario)
python manage.py createsuperuser 
para poder entrar a la url /admin

# Ejecutar el servidor de desarrollo
python manage.py runserver