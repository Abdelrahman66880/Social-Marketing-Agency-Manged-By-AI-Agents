from fastapi import APIRouter, HTTPException, status, Request, Depends, Body
from fastapi.responses import JSONResponse
from typing import Optional, Dict
from src.models.BuisnessInfoModel import BusinessInfoModel
from src.models.db_schemas.BuisnessInfo import BuisnessInfo
from src.models.enums.ResponseSignal import ResponseSignal

business_info_router = APIRouter(
    prefix="/business-info",
    tags=["Business Info"]
)

async def get_business_model(request: Request) -> BusinessInfoModel:
    """
    Dependency to get a BusinessInfoModel instance.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        BusinessInfoModel: An initialized model instance.
    """
    db_client = request.app.db_client
    return await BusinessInfoModel.create_instance(db_client)


@business_info_router.get(
    "/users/{user_id}",
    response_model=BuisnessInfo,
    status_code=status.HTTP_200_OK
)
async def get_business_info(
    user_id: str,
    model: BusinessInfoModel = Depends(get_business_model)
):
    """
    Get Business Info by user_id.

    Args:
        user_id (str): User's ObjectId or string ID.
        model (BusinessInfoModel): The database model dependency.

    Returns:
        BuisnessInfo: The business info document.

    Raises:
        HTTPException: If the business info is not found (404).
    """
    info = await model.get_by_user_id(user_id)
    
    if not info:
        # We can use HTTPException here for standard 404, or JSONResponse if strict signal needed.
        # usually 404 for GET is clean as Exception.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=ResponseSignal.BUSINESS_INFO_NOT_FOUND.value
        )
    
    return info


@business_info_router.post(
    "/",
    status_code=status.HTTP_201_CREATED
)
async def create_business_info(
    business_info: BuisnessInfo,
    model: BusinessInfoModel = Depends(get_business_model)
):
    """
    Create a new BusinessInfo document.

    Args:
        business_info (BuisnessInfo): The payload containing business details.
        model (BusinessInfoModel): The database model dependency.

    Returns:
        JSONResponse: A response containing the success signal and inserted ID.

    Raises:
        HTTPException: If business info already exists (400).
    """
    if await model.exists_for_user(str(business_info.user_id)):
         return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.BUSINESS_INFO_ALREADY_EXISTS.value
            }
        )

    inserted_id = await model.create_business_info(business_info)
    
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "signal": ResponseSignal.BUSINESS_INFO_CREATED.value,
            "id": str(inserted_id)
        }
    )


@business_info_router.put(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK
)
async def update_business_info(
    user_id: str,
    business_info: BuisnessInfo,
    model: BusinessInfoModel = Depends(get_business_model)
):
    """
    Replace/Update Business Info for a user.

    Args:
        user_id (str): The user ID (must match the ID in the body/logic).
        business_info (BuisnessInfo): The new data to replace existing info.
        model (BusinessInfoModel): The database model dependency.

    Returns:
        JSONResponse: A response containing the success signal.

    Raises:
        HTTPException: If Business Info is not found (404).
    """
    # Ensure the body matches the path user_id for consistency
    business_info.user_id = user_id
    
    result = await model.replace_business_info(user_id, business_info)
    
    if result["matched_count"] == 0:
         return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignal.BUSINESS_INFO_NOT_FOUND.value
            }
        )
         
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.BUSINESS_INFO_UPDATED.value
        }
    )


@business_info_router.patch(
    "/users/{user_id}/token",
    status_code=status.HTTP_200_OK,
    description="Manually update Facebook Page ID and Token."
)
async def update_facebook_token(
    user_id: str,
    page_id: str = Body(..., embed=True),
    token: str = Body(..., embed=True),
    model: BusinessInfoModel = Depends(get_business_model)
):
    """
    Update just the Facebook Page ID and Token.

    Args:
        user_id (str): The user ID.
        page_id (str): The new Facebook Page ID.
        token (str): The new Access Token.
        model (BusinessInfoModel): The database model dependency.

    Returns:
        JSONResponse: A response containing the success signal.

    Raises:
        HTTPException: If Business Info is not found (404).
    """
    if not await model.exists_for_user(user_id):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignal.BUSINESS_INFO_NOT_FOUND.value
            }
        )
        
    await model.update_business_info(
        user_id,
        {
            "facebook_page_id": page_id,
            "facebook_page_access_token": token
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.FACEBOOK_CREDENTIALS_UPDATED.value
        }
    )
