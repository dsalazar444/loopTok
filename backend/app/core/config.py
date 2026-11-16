# encargado de centralizar y validar configuracion y envs del back
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256" # valor opcional que este en .env, si no, toma por default
    access_token_expire_minutes: int = 60
    session_inactivity_minutes: int = 10 
    frontend_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict( # config interna de pydantic
        env_file=".env",
        extra="ignore",
    )


@lru_cache # es para que resultado de esta funcion, se guarde en cache, y no haya que leer por cada request, el env
def get_settings() -> Settings:
    return Settings()
