from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from bson import ObjectId
from datetime import datetime, timezone

class Notification(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")

    title: str = Field(..., min_length= 10, max_length=100, description="title of the recommendation filled by Ai agent")

    content: str = Field(..., min_length=10)

    seen: bool = Field(default=False)

    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user_id: ObjectId


    @field_validator('id', mode="after")
    def validate_post_id(cls, value):
        if not isinstance(value, ObjectId):
            raise ValueError("Notification_id must be a valid ObjectId")
        return value
    
    model_config = ConfigDict(arbitrary_types_allowed=True)



    @classmethod
    def get_indexes(cls):
        return [
            {"key": [("user_id", 1)], "name": "user_index", "unique": False},
            {"key":[("createdAt", -1)], "name":"createdAt", "unique": False}
        ]
