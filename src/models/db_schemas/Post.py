from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime
from ..enums.UserEnums import PostStatus
class Post(BaseModel):
    """Schema for a Post document in the database."""
    id : Optional[ObjectId] = Field(None, alias="_id")
    userFeedback: float = Field(
        default=0.0,
        ge=0.0,
        le=5.0,
        description="User feedback rating (0.0 to 5.0) on the AI agent's response."
    )
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    
    title: str = Field(..., min_length=3, max_length=100)

    content: str = Field(
        ...,
        min_length=100,
        description="The main content of the post."
    )
    comments: Optional[list[str]] = []
    status: PostStatus = Field(
        default=PostStatus.DRAFT,
        description="The status of the post, one of: DRAFT, ACCEPTED, or REJECTED."
    )
    
    @field_validator('id', mode="after")
    def validate_post_id(cls, value):
        if not isinstance(value, ObjectId):
            raise ValueError("post_id must be a valid ObjectId")
        return value
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("post_id", 1)],
                "name": "post_index",
                "unique": False,
            },
        ]
    