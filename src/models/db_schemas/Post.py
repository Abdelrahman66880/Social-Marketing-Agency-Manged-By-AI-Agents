from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime
from ..enums.UserEnums import PostStatus
class Post(BaseModel):
    """Schema for a Post document in the database."""
    id : Optional[ObjectId] = Field(None, alias="_id")
    isAccepted: bool = False
    userRate: float
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    title: str
    category: str
    content: str = Field(
        ...,
        min_length=100,
        description="The main content of the post."
    )
    updatedcontent: Optional[str] = Field(
        None,
        min_length=100,
        description="The updated content of the post."
    )
    updatedAt: datetime

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
    