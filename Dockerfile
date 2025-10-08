# Imagen base oficial de Python
FROM python:3.12-slim

# Establecer directorio de trabajo
WORKDIR /app

# Evitar que Python genere archivos .pyc y mejorar logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=project.settings
ENV DJANGO_DEBUG=0

# Instalar dependencias del sistema necesarias para psycopg2, Pillow, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . .

# Copiar entrypoint y darle permisos de ejecución
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Exponer el puerto (Gunicorn servirá en 8000)
EXPOSE 8000

# Usar el entrypoint que correrá migraciones y luego levanta Gunicorn
ENTRYPOINT ["/app/entrypoint.sh"]
