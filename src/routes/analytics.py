# -----------------------------------
# Analytics Routes
# -----------------------------------
from fastapi import APIRouter, status, Depends, HTTPException, Request, Path
from typing import List
from src.models.db_schemas.Recommendation import Recommendation
from src.models.db_schemas.Analysis import Analysis
from src.models.RecommendationModel import RecommendationModel
from src.models.AnalysisModel import AnalysisModel
from src.models.enums.ResponseSignal import ResponseSignal


# -----------------------------------
# Router Initialization
# -----------------------------------
analytics_router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


# -----------------------------------
# Dependency Injection
# -----------------------------------
async def get_recommendation_model(request: Request) -> RecommendationModel:
    """
    Retrieve a `RecommendationModel` instance for database operations.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        RecommendationModel: An initialized RecommendationModel instance connected to the database.
    """
    db_client = request.app.db_client
    return await RecommendationModel.create_instance(db_client)


async def get_analysis_model(request: Request) -> AnalysisModel:
    """
    Retrieve a `AnalysisModel` instance for database operations.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        AnalysisModel: An initialized AnalysisModel instance connected to the database.
    """
    db_client = request.app.db_client
    return await AnalysisModel.create_instance(db_client)


# -----------------------------------
# Recommendation Endpoints
# -----------------------------------
@analytics_router.post(
    "/recommendations",
    status_code=status.HTTP_201_CREATED,
    response_model=Recommendation
)
async def post_recommendations(
    req: Recommendation,
    recommendation_model: RecommendationModel = Depends(get_recommendation_model)
):
    """
    Add a recommendation to the database.
    
    Args:
        req: A Recommendation database schema.
    """
    recs = await recommendation_model.create_recommendation(req)
    req.id = str(recs)
    return req


@analytics_router.get(
    "/users/{user_id}/recommendations/{limit}/{skip}",
    response_model=List[Recommendation],
    status_code=status.HTTP_200_OK
)
async def get_recommendations(
    user_id: str,
    limit: int = Path(..., ge=1, le=100, description="Maximum number of recommendations to return."),
    skip: int = Path(..., ge=0, description="Number of recommendations to skip for pagination."),
    recommendation_model: RecommendationModel = Depends(get_recommendation_model)
):
    """
    Get all recommendations associated with a user ID.

    Args:
        user_id: The user ID.
        limit: Pagination limit.
        skip: Pagination offset.

    Returns:
        All recommendations associated with the user ID.
    """
    recs = await recommendation_model.get_by_user_id(user_id=user_id, limit=limit, skip=skip)
    if not recs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignal.RECOMMENDATION_NOT_FOUND.value
        )
    return recs


# -----------------------------------
# Analysis Endpoints
# -----------------------------------
@analytics_router.post(
    "/analysis",
    status_code=status.HTTP_201_CREATED,
    response_model=Analysis
)
async def post_analysis(
    req: Analysis,
    analysis_model: AnalysisModel = Depends(get_analysis_model)
):
    """
    Add an analysis document to the database.
    
    Args:
        req: An Analysis database schema.
    """
    recs = await analysis_model.create_analysis(analysis=req)
    req.id = str(recs)
    return req


@analytics_router.get(
    "/users/{user_id}/analysis/competitor/{limit}/{skip}",
    response_model=List[Analysis],
    status_code=status.HTTP_200_OK
)
async def get_competitor_analysis(
    user_id: str,
    limit: int = Path(..., ge=1, le=100, description="Maximum number of competitor analyses to return."),
    skip: int = Path(..., ge=0, description="Number of analyses to skip for pagination."),
    analysis_model: AnalysisModel = Depends(get_analysis_model)
):
    """
    Get all competitor analysis documents associated with a user ID.

    Args:
        user_id: The user ID.
        limit: Pagination limit.
        skip: Pagination offset.

    Returns:
        All competitor analyses associated with the user ID.
    """
    recs = await analysis_model.get_competitor_analysis_by_user_id(user_id=user_id, skip=skip, limit=limit)
    if not recs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignal.COMPETITOR_ANALYSIS_NOT_FOUND.value
        )
    return recs


@analytics_router.get(
    "/users/{user_id}/analysis/interaction/{limit}/{skip}",
    response_model=List[Analysis],
    status_code=status.HTTP_200_OK
)
async def get_interaction_analysis(
    user_id: str,
    limit: int = Path(..., ge=1, le=100, description="Maximum number of interaction analyses to return."),
    skip: int = Path(..., ge=0, description="Number of analyses to skip for pagination."),
    analysis_model: AnalysisModel = Depends(get_analysis_model)
):
    """
    Get all interaction analysis documents associated with a user ID.

    Args:
        user_id: The user ID.
        limit: Pagination limit.
        skip: Pagination offset.

    Returns:
        All interaction analyses associated with the user ID.
    """
    recs = await analysis_model.get_interaction_analysis_by_user_id(user_id=user_id, skip=skip, limit=limit)
    if not recs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignal.INTERACTION_ANALYSIS_NOT_FOUND.value
        )
    return recs
