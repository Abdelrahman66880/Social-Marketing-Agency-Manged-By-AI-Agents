from pydantic import BaseModel
from typing import Optional, List


class InteractionResponse(BaseModel):
    page_id: str
    analyzed_at: str
    total_posts: int
    total_comments: int
    total_messages: int
    sentiment_breakdown: dict