# repositorio concentra las operaciones de persistencia.
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.users.models import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(
            User.username == username
        )

        return self.session.scalar(statement)

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
