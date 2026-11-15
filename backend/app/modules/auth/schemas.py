import re
from pydantic import BaseModel, Field, ConfigDict, field_validator

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9._]+$")
FULL_NAME_PATTERN = re.compile(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$")

class RegisterRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    full_name: str = Field(min_length=2, max_length=100, alias="fullName")
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("full_name", mode="before") #mode(before) porque queremos normalizar datos antes de comprobar longitud (se ejeucta antes de comprobar reglas de Field(...))
    @classmethod
    def normalize_full_name(cls, value: str) -> str:
        if not isinstance(value, str) or not FULL_NAME_PATTERN.fullmatch(value):
            raise ValueError("Invalid full name format")

        return " ".join(value.split())

    @field_validator("username", mode="before")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Username must be a string")

        return value.strip().lower()

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not USERNAME_PATTERN.fullmatch(value):
            raise ValueError("Invalid username format")

        return value


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)

    @field_validator("username", mode="before")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Username must be a string")

        return value.strip().lower()


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int