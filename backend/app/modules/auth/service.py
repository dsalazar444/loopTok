from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import UsernameAlreadyExistsError
from app.core.security import hash_password
from app.modules.auth.schemas import RegisterRequest
from app.modules.users.models import User
from app.modules.users.repository import UserRepository

class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.user_repository = UserRepository(session)

    def register(self, request: RegisterRequest) -> User:
        existing_user = self.user_repository.get_by_username(
            request.username
        )

        if existing_user is not None:
            raise UsernameAlreadyExistsError()

        password_hash = hash_password(request.password)

        user = self.user_repository.create(
            full_name=request.full_name,
            username=request.username,
            password_hash=password_hash,
        )

        try:
            self.session.commit()
        except IntegrityError: # Restricción de la bd -> se intenta guardar mismo usuario al "mismo" tiempo -> Choca con restriccion UNique           
            self.session.rollback()
            raise UsernameAlreadyExistsError() from None

        self.session.refresh(user) # Consulta nuevamente la base de datos para traer los valores reales recién generados -> para retornar object con timestamps de createdat... porque esos los genera la bd

        return user
