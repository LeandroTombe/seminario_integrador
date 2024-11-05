# Usa una imagen base de Python
FROM python:3.12



# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo de dependencias (requirements.txt) al contenedor
COPY requirements.txt /app/

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev gcc mariadb-client && \
    rm -rf /var/lib/apt/lists/*

# Copia el resto del código del proyecto al contenedor
COPY . /app

# Expone el puerto en el que Django correrá
EXPOSE 8000

# Ejecuta el comando para iniciar el servidor de Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
