from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.modules.users.router import router as users_router
from app.modules.auth.router import router as auth_router
from app.modules.videos.router import router as videos_router
from app.modules.likes.router import router as likes_router
from app.modules.not_interested.router import router as not_interested_router


settings = get_settings()

app = FastAPI(title="LoopTok API")

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


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
