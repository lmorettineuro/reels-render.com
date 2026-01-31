# Usamos una imagen ligera de Python
FROM python:3.9-slim

# INSTALACIÓN CLAVE: Instalamos FFmpeg, ImageMagick y fuentes
# Sin esto, MoviePy fallará al intentar poner texto
RUN apt-get update && \
    apt-get install -y ffmpeg imagemagick libmagick++-dev fonts-liberation && \
    apt-get clean

# Configuración técnica para permitir a ImageMagick procesar texto (seguridad)
RUN sed -i 's/none/read,write/g' /etc/ImageMagick-6/policy.xml

# Preparamos la carpeta
WORKDIR /app

# Copiamos e instalamos librerías de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos tu código
COPY . .

# Comando de inicio (con timeout de 120s para que no corte el video a medias)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--timeout", "120"]
