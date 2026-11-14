from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# permite convertir una instancia User de SQLAlchemy en una respuesta JSON
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True) # sesion devuelve modelo sqlalchemy, con esto le enseñamos a pydantic a extraer datos de él (solo sabe leer dict)

    id: UUID
    full_name: str = Field(serialization_alias="fullName")
    username: str
    created_at: datetime = Field(serialization_alias="createdAt")
