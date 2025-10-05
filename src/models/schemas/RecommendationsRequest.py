from pydantic import BaseModel, Field
from typing import List, Optional


class RecommendationsRequest(BaseModel):
    """
    Input schema for generating recommendations.
    """
    page_id: str = Field(..., description="Facebook Page ID to analyze")
    page_access_token: str = Field(..., description="Page access token with required permissions")
    business_profile: Optional[dict] = Field(
        None,
        description="Optional business metadata (industry, competitors, tone, goals, etc.)"
    )