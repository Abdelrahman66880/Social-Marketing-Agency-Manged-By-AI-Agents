from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Recommendation(BaseModel):
    """
    Represents a single AI-generated recommendation.
    """
    title: str = Field(..., description="Short title summarizing the recommendation")
    description: str = Field(..., description="Detailed explanation of the recommendation")