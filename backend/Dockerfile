# imagen base de python
FROM python:3.12-slim
WORKDIR /app

# primero las dependencias (así Docker no las reinstala si solo cambia el código)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# código del backend, migraciones y scripts
COPY alembic.ini .
COPY app/ ./app/
COPY migrations/ ./migrations/
COPY scripts/ ./scripts/

EXPOSE 8000

# la misma imagen sirve para el backend y para las migraciones (el compose cambia el comando)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
