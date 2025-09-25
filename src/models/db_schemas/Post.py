from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime

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
        max_length=1000,
        description="The main content of the post (100-1000 characters)."
    )
    updatedcontent: Optional[str] = Field(
        None,
        min_length=100,
        max_length=1000,
        description="The updated content of the post (100-1000 characters)."
    )
    
    comments: Optional[list[str]] = []
    updatedAt: datetime
    
    @validator('id')
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
    