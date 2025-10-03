from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from src.models.enums.UserEnums import PostStatus


# ---------- RESPONSE SCHEMAS ----------
class PostResponse(BaseModel):
    id: str
    title: str
    content: str
    createdAt: datetime
    status: PostStatus
    comments: List[str] = []
    userFeedback: float

    @field_validator("id", mode="before")
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v


class EditPostResponse(BaseModel):
    id: str
    title: str
    content: str


class ApproveDraftResponse(BaseModel):
    id: str
    status: PostStatus


class RejectDraftResponse(BaseModel):
    id: str
    status: PostStatus


# ---------- REQUEST SCHEMAS ----------
class CreatePostRequest(BaseModel):
    title: str
    content: str = Field(
        ...,
        min_length=100,
        description="The main content of the post."
    )


class EditPostRequest(BaseModel):
    post_id: str
    new_title: str = Field(..., min_length=3, max_length=100)
    new_content: str = Field(..., min_length=100)


class ApproveDraftRequest(BaseModel):
    post_id: str


class RejectDraftRequest(BaseModel):
    post_id: str
