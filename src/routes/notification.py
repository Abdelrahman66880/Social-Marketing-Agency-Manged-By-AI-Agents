from fastapi import APIRouter, status, Request, Depends, HTTPException, Query
from src.models.NotificationModel import NotificationModel
from src.models.db_schemas.Notification import Notification
from bson import ObjectId, errors
from typing import List
from src.models.enums.ResponseSignal import ResponseSignal
from src.models.schemas.NotificationSchemas import (
    MarkReadRequest,
    SendNotificationRequest,
    MarkReadResponse,
)
notification_route = APIRouter(prefix="/notification", tags=["Notification"])

async def get_notification_model(request: Request) -> NotificationModel:
    """
    Dependency to get a NotificationModel instance from the app's database client.
    """
    db_client = request.app.db_client
    return await NotificationModel.create_instance(db_client)


@notification_route.get(
    "/get_all_user_notifications",
    status_code=status.HTTP_200_OK,
    response_model=List[Notification]
)
async def get_all_user_notification(
    user_id : str = Query(description="User ID"),
    limit: int = Query(50, description="Maximum number of notifications to fetch. Defaults to 50"),
    notification_model: NotificationModel = Depends(get_notification_model)
) -> List[Notification]:
    try:
        result = await notification_model.get_user_notifications(user_id, limit=limit)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ResponseSignal.NOTIFICATION_NOT_FOUND.value
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notifications: {str(e)}"
        )


@notification_route.put(
    "/mark_seen",
    response_model=MarkReadResponse,
    status_code=status.HTTP_200_OK
)
async def mark_read(
    req: MarkReadRequest,
    notification_model: NotificationModel = Depends(get_notification_model)
) -> MarkReadResponse:
    try:
        result = await notification_model.mark_as_seen(req.notification_id)
        if result.get("matched_count", 0) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ResponseSignal.NOTIFICATION_NOT_FOUND.value
            )
        return MarkReadResponse(
            matched_count=result["matched_count"],
            modified_count=result["modified_count"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseSignal.FAILED_TO_MARK_AS_READ.value
        )


@notification_route.post(
    "/send",
    response_model=Notification,
    status_code=status.HTTP_201_CREATED
)
async def send_notification(
    req: SendNotificationRequest,
    notification_model: NotificationModel = Depends(get_notification_model)
) -> Notification:
    try:
        # Validate user_id
        try:
            user_obj_id = ObjectId(req.user_id)
        except errors.InvalidId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ResponseSignal.INVALID_USER_ID.value
            )

        notification = Notification(
            title=req.title,
            content=req.content,
            user_id=user_obj_id
        )
        result = await notification_model.create_notification(notification=notification)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send notification: {str(e)}"
        )
