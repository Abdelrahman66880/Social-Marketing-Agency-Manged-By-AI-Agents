# Analytics routes
from fastapi import APIRouter, status, Depends, HTTPException
from typing import Optional, List, Dict, Any
from ..controllers.analytics import AnalyticsController
from models.schemas import InteractionsResponse, CompetitorRequest, CompetitorSummary

analytics_router = APIRouter(
    prefix="/analytics", 
    tags=["Analytics"]
)


async def get_analysis_interaction(page_id: str, page_access_token: str) -> Dict[str, Any]:
    """
    Fetches and analyzes interactions for a given Facebook page.
    
    Args:
        page_id (str): The Facebook page ID.
        page_access_token (str): The access token for the Facebook page.
        
    Returns:
        Dict[str, Any]: A dictionary containing analyzed interaction data.
    """
    try:
        analyst = AnalyticsController()
        result = await analyst.analyze_interaction_by_page_id(page_id=page_id, page_access_token=page_access_token)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
