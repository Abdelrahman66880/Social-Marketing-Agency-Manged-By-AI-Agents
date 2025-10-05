# Analytics routes
from fastapi import APIRouter, status, Depends, HTTPException
from typing import Optional, List, Dict, Any
from ..controllers.analytics import AnalyticsController
from models.schemas import InteractionsResponse, CompetitorRequest, CompetitorSummary
from models.schemas.Recommendation import Recommendation
from models.schemas.RecommendationsRequest import RecommendationsRequest

analytics_router = APIRouter(
    prefix="/analytics", 
    tags=["Analytics"]
)

@analytics_router.get("/interactions", response_model=InteractionsResponse)
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


@analytics_router.get("/competitors", response_model=List[CompetitorSummary])
async def get_competitors_analytics(key_words: str, page_access_token: str, max_pages: int = 5):
    """
    Monitor Competitors unsing Keywords
    """
    try:
        key_words_list = [
            k.strip()
            for k in key_words.split(",") if k.strip()
        ]
        result = await AnalyticsController.analyze_competitors(
            key_words_list=key_words_list,
            page_access_token=page_access_token,
            max_pages= max_pages
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@analytics_router.post("/recommendations", response_model=List[Recommendation])
async def post_recommendations(req: RecommendationsRequest):
    """
    Generate AI-powered recommendations based on interaction & competitor data.
    """
    try:
        recs = await AnalyticsController.generate_recommendations(
            req.page_id, 
            req.page_access_token, 
            req.business_profile
        )
        return recs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))