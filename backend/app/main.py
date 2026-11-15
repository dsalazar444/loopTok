from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.modules.users.router import router as users_router
from app.modules.auth.router import router as auth_router
from app.modules.videos.router import router as videos_router

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


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


# shortcut: sirve los mp4 locales de pint/test/out/videos solo para pruebas, reemplazar por GET /videos/{id}/playback con S3/MinIO
_dev_videos = Path(__file__).resolve().parents[3] / "test" / "out" / "videos"
if _dev_videos.is_dir():
    app.mount("/dev-media", StaticFiles(directory=_dev_videos), name="dev-media")
