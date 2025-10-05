from pydantic import BaseModel, Field, field_validator, ConfigDict, BeforeValidator
from typing import Optional, Annotated
from bson.objectid import ObjectId
from datetime import datetime
from ..enums.PostEnums import PostStatus

PyObjectId = Annotated[str, BeforeValidator(str)]
class Post(BaseModel):
    """Schema for a Post document in the database."""
    id : Optional[PyObjectId] = Field(None, alias="_id")
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

    user_id: PyObjectId
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "66fe9e7fbd12f8f9c9f3e3a1",
                "title": "AI in Healthcare: Opportunities and Challenges",
                "content": "Artificial Intelligence is transforming the healthcare industry by improving diagnostics, treatment recommendations, and patient outcomes. However, challenges remain in terms of data privacy and interpretability of AI models...",
                "userFeedback": 4.7,
                "comments": [
                    "This is an insightful post!",
                    "AI ethics should be discussed more here."
                ],
                "status": "DRAFT",
                "createdAt": "2025-10-05T14:00:00Z",
                "user_id": "66fe9e7fbd12f8f9c9f3e3d2"
            }
        }
        )
    
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("post_id", 1)],
                "name": "post_index",
                "unique": False,
            },
        ]
    