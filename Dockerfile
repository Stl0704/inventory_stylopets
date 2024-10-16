# Usar una imagen base de Python
FROM python:3.12-slim

# Instalar dependencias del sistema necesarias para mysqlclient y zbar
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev build-essential pkg-config libzbar-dev

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos de tu proyecto al contenedor
COPY . /app

# Instalar las dependencias del proyecto
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# # Copia el script wait-for-it
# COPY wait-for-it.sh /wait-for-it.sh
# RUN chmod +x /wait-for-it.sh

# Expone el puerto 8000 para que Django esté disponible
EXPOSE 8000

# Comando para ejecutar las migraciones y luego iniciar el servidor
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]