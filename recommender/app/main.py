from fastapi import FastAPI

from app.modules.recommender.router import router as recommender_router

app = FastAPI(title="Recommender API")

# routes
app.include_router(recommender_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
