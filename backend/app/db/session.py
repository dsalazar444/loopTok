# gestiona las conexiones y sesiones con la bd 
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


engine = create_engine( # motor de conexion
    get_settings().database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker( # constructor de sesiones, usando motor -> cada vez que se hace peticion http
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def get_db_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
