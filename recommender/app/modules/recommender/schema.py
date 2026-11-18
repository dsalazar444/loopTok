from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class PlaybackEventType(str, Enum):
    STARTED = "video_started"
    IN_PROGRESS = "video_progress"
    COMPLETED = "video_completed"
    ABANDONED = "video_abandoned"


class AbandonReason(str, Enum):
    NAVIGATION = "navigation"
    UNMOUNT = "unmount"


# El evento tal como lo envía el frontend (claves en camelCase -> alias)
class EventRequest(BaseModel):
    event_id: UUID = Field(alias="eventId")
    event_type: PlaybackEventType = Field(alias="eventType")
    playback_id: UUID = Field(alias="playbackId")
    video_id: str = Field(alias="videoId")
    timestamp: datetime

    watch_time_ms: int = Field(alias="watchTimeMs", ge=0)
    position_seconds: float = Field(alias="positionSeconds", ge=0)
    duration_seconds: float = Field(alias="durationSeconds", ge=0)
    max_progress_percent: float = Field(alias="maxProgressPercent", ge=0, le=100)

    is_replay: bool = Field(alias="isReplay")
    play_count: int = Field(alias="playCount", ge=0)

    reason: AbandonReason | None = None
    milestone_percent: float | None = Field(default=None, alias="milestonePercent")

    category: str


# Evento tal como se guarda en Kafka -> EventRequest + user_id (lo añade el backend)
class KafkaEvent(EventRequest):
    user_id: UUID = Field(alias="userId")
