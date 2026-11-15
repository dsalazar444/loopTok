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

## conectarse a bd
```cmd
docker exec -it backend-postgres-1 psql -U looptok -d looptok
```
Para listar tablas, podemos usar \dt, y para salir \q