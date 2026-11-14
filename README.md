# React + TypeScript + Vite

# Correrla
## frontend:
```cmd
npm install
npm run dev
```

## backend: linea 3 corre migraciones 
```cmd
source .venv/bin/activate
docker compose up -d
alembic upgrade head
uvicorn main:app --reload
```

## para añadir nueva migración:
```cmd
# crea archivo con cambios, en versions/
alembic revision --autogenerate -m "descripción de lo que cambió" 
alembic upgrade head
```