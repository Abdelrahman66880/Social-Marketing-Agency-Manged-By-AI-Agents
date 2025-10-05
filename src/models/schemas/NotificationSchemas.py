from pydantic import BaseModel, Field
class SendNotificationRequest(BaseModel):
    user_id: str

    title: str = Field(..., min_length= 10, max_length=100, description="title of the recommendation filled by Ai agent")

    content: str = Field(..., min_length=10)

class MarkReadRequest(BaseModel):
    notification_id: str


class MarkReadResponse(BaseModel):
    matched_count: int
    modified_count: int
