from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class VideoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    category: str
    subcategory: str | None
    language: str
    duration_seconds: int = Field(serialization_alias="durationSeconds")
    creator: str | None
    tags: list[str]
    upload_date: date | None = Field(serialization_alias="uploadDate")
    url: str 
        
    likes_count: int = Field(
    default=0,
    serialization_alias="likesCount",
    )

    is_liked: bool = Field(
        default=False,
        serialization_alias="isLiked",
    )


class VideoListResponse(BaseModel):
    items: list[VideoResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")
