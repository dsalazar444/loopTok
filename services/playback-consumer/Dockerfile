# ponemos imagen abse de python
FROM python:3.12-slim

#directorio de trabajo dentro del contenedor
WORKDIR /app


# el contexto de build es la carpeta del servicio (ver compose.yaml)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copiar el codigo del consumer
COPY app/ ./app/

CMD ["python", "-m", "app.kafka_consumer"]
