from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.kafka_producer import close_kafka_producer, init_kafka_producer
from app.modules.users.router import router as users_router
from app.modules.auth.router import router as auth_router
from app.modules.videos.router import router as videos_router
from app.modules.likes.router import router as likes_router
from app.modules.not_interested.router import router as not_interested_router
from app.modules.sessions.router import router as sessions_router
from app.modules.events.router import router as events_router


settings = get_settings()

# lifespan: código que corre una vez al encender y una vez al apagar la app
@asynccontextmanager
async def lifespan(_: FastAPI):
    # Al encender -> crea el Producer de Kafka -> Se hace aquí para tener uno solo.
    # Si KAFKA_REQUIRED=true y falta KAFKA_BOOTSTRAP_SERVERS, la app no arranca
    init_kafka_producer()
    yield  # aquí la app queda funcionando
    # Al apagar -> envía los eventos que aún estaban pendientes y cierra el Producer
    close_kafka_producer()


app = FastAPI(title="LoopTok API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
# routes
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(videos_router)
app.include_router(likes_router)
app.include_router(not_interested_router)
app.include_router(sessions_router)
app.include_router(events_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
