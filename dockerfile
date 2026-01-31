FROM python:3.9-slim

# Instalamos dependencias
RUN apt-get update && \
    apt-get install -y ffmpeg imagemagick libmagick++-dev fonts-liberation && \
    apt-get clean

# --- CORRECCIÓN AQUÍ ---
# En lugar de buscar una carpeta fija, buscamos el archivo "policy.xml" donde sea 
# que lo haya instalado el sistema y aplicamos el permiso de escritura.
RUN find /etc -name "policy.xml" -exec sed -i 's/none/read,write/g' {} +

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--timeout", "120"]
