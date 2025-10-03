from pydantic import BaseModel
from typing import Optional, List


class CompetitorRequest(BaseModel):
    """Request model for competitor pages analysis."""
    keywords: List[str]
    num_pages: Optional[int] = 3 # number of competitor pages 
