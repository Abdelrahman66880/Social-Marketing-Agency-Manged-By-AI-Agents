from pydantic import BaseModel, Field
from src.models.enums.PostEnums import PostStatus


# ---------- RESPONSE SCHEMAS ----------
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
    user_id: str

class EditPostRequest(BaseModel):
    new_title: str = Field(..., min_length=3, max_length=100)
    new_content: str = Field(..., min_length=100)
