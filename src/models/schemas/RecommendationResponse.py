from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class RecommendationsResponse(BaseModel):
    """
    Full response schema returned by the /analysis/recommendations endpoint.
    """
    page_id: str
    recommendations: List[Recommendation]