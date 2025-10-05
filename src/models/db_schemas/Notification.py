from typing import Optional, Annotated
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator
from datetime import datetime, timezone

PyObjectId = Annotated[str, BeforeValidator(str)]

class Notification(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    title: str = Field(..., min_length=10, max_length=100, description="Title of the recommendation filled by AI agent")
    content: str = Field(..., min_length=10)
    seen: bool = Field(default=False)
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: PyObjectId

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "_id": "66fe9e7fbd12f8f9c9f3e3d1",
                "title": "New AI Recommendation",
                "content": "We found a great new resource for you.",
                "seen": False,
                "createdAt": "2025-10-05T12:30:00Z",
                "user_id": "66fe9e7fbd12f8f9c9f3e3d2"
            }
        }
    )

    @classmethod
    def get_indexes(cls):
        return [
            {"key": [("user_id", 1)], "name": "user_index", "unique": False},
            {"key": [("createdAt", -1)], "name": "createdAt", "unique": False},
        ]
