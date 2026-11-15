# repositorio concentra las operaciones de persistencia.
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.videos.models import Video


class VideoRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_paginated(
        self,
        *,
        page: int,
        page_size: int,
        category: str | None = None,
    ) -> tuple[list[Video], int]:
        statement = select(Video)
        count_statement = select(func.count()).select_from(Video)

        if category is not None:
            statement = statement.where(Video.category == category)
            count_statement = count_statement.where(Video.category == category)

        total = self.session.scalar(count_statement) or 0

        items = self.session.scalars(
            statement
            .order_by(Video.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()

        return list(items), total
