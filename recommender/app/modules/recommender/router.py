from fastapi import APIRouter, Depends, status
from app.modules.recommender.schema import KafkaEvent
from app.modules.recommender.service import RecommenderService


router = APIRouter(
    prefix="/recommend",
    tags=["recommendations"],
)

@router.post(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
def process_event(event: KafkaEvent) -> None:

    service = RecommenderService(event=event)
    service.generate_recommendation()

