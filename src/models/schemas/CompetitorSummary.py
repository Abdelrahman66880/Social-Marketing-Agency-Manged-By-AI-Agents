from pydantic import BaseModel
from typing import Optional, List

class CompetitorSummary(BaseModel):
    page_id: str
    page_name: str
    total_likes: int
    total_followers: int
    top_posts: List[dict]  # List of top posts with details like post_id, likes, comments, shares