# repositorio concentra las operaciones de persistencia.
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.users.models import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session # recibe y asigna sesión para conexión a bd -> self.session es el objeto de SQLAlchemy que se comunica directamente con PostgreSQL

    def get_by_id(self, user_id: UUID) -> User | None:
        return self.session.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(
            User.username == username
        )

        return self.session.scalar(statement) # devuelve objeto sqlalchemy si existe

    def create(
        self,
        *,
        full_name: str,
        username: str,
        password_hash: str,
    ) -> User:
        user = User(
            full_name=full_name,
            username=username,
            password_hash=password_hash,
        )

        self.session.add(user)

        return user
        
# Observa que create() utiliza session.add(), pero no ejecuta commit().
# Esto es intencional: dejaremos que el servicio controle cuándo confirmar la transacción.
# Así mantenemos separados el acceso a datos y la lógica de negocio   