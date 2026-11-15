# repositorio concentra las operaciones de persistencia.
from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session, InstrumentedAttribute
from typing import Any
from uuid import UUID

from app.modules.dislikes.models import Dislike
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
        user_id: UUID | None = None,
    ) -> tuple[list[Video], int]:
        statement = select(Video)
        count_statement = select(func.count()).select_from(Video)

        if category is not None:
            statement = statement.where(Video.category == category)
            count_statement = count_statement.where(Video.category == category)

        # hide videos this user marked as "not interested"; applied to the count too so pagination stays right
        if user_id is not None:
            not_disliked = ~exists().where(
                Dislike.video_id == Video.id,
                Dislike.user_id == user_id,
            )
            statement = statement.where(not_disliked)
            count_statement = count_statement.where(not_disliked)

        total = self.session.scalar(count_statement) or 0

        items = self.session.scalars(
            statement
            .order_by(Video.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()

        return list(items), total

    # return first result -> util for id
    def get_by( 
        self,
        column: InstrumentedAttribute[Any],
        value: object,
    ) -> Video | None:
        statement = select(Video).where(column == value)

        return self.session.scalars(statement).first()
