# Usa una imagen base oficial de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de dependencia
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de la aplicación
# Asumiendo que tu estructura incluye la carpeta 'backend'
COPY . /app

# Expone el puerto que usa Uvicorn
EXPOSE 8000

# Define la variable de entorno para producción
ENV PYTHONUNBUFFERED=1

# Comando para iniciar el servidor FastAPI con Uvicorn
# El formato es: uvicorn <nombre_del_modulo>:<nombre_del_objeto_fastapi> --host 0.0.0.0 --port 8000
CMD ["uvicorn", "backend.agent_server:app", "--host", "0.0.0.0", "--port", "8000"]