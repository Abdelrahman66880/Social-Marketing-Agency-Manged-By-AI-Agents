from pydantic import BaseModel, Field
class SendNotificationRequest(BaseModel):
    user_id: str

    title: str = Field(..., min_length= 10, max_length=100, description="title of the recommendation filled by Ai agent")

    content: str = Field(..., min_length=10)

class MarkReadResponse(BaseModel):
    notification_id: str
    modified_count: int
