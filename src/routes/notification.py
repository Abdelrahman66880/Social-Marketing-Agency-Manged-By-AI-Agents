from fastapi import APIRouter, status, Request, Depends, HTTPException, Query
from typing import List
from src.models.NotificationModel import NotificationModel
from src.models.db_schemas.Notification import Notification
from src.models.enums.ResponseSignal import ResponseSignal
from src.models.schemas.NotificationSchemas import (
    MarkReadResponse,
)

notification_route = APIRouter(prefix="/notifications", tags=["Notification"])


# ======================================================================================
# Dependency
# ======================================================================================
async def get_notification_model(request: Request) -> NotificationModel:
    """
    Dependency to initialize and return a `NotificationModel` instance using the app's database client.

    Args:
        request (Request): The incoming FastAPI request containing the app context and database client.

    Returns:
        NotificationModel: An initialized model instance connected to the database.
    """
    db_client = request.app.db_client
    return await NotificationModel.create_instance(db_client)


# ======================================================================================
# Routes
# ======================================================================================
@notification_route.get(
    "/users/{user_id}/{limit}/{skip}",
    status_code=status.HTTP_200_OK,
    response_model=List[Notification],
)
async def get_all_user_notification(
    user_id: str,
    limit: int,
    skip: int,
    notification_model: NotificationModel = Depends(get_notification_model),
) -> List[Notification]:
    """
    Retrieve all notifications for a specific user.

    Args:
        user_id (str): The MongoDB ObjectId of the user whose notifications will be retrieved.
        limit (int, optional): Maximum number of notifications to fetch. Defaults to 50.
        notification_model (NotificationModel): Dependency-injected model for database operations.

    Returns:
        List[Notification]: A list of user notifications.

    Raises:
        HTTPException(404): If no notifications are found.
        HTTPException(500): If database query fails.
    """
    try:
        result = await notification_model.get_user_notifications(user_id, limit=limit, skip=skip)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail= ResponseSignal.NOTIFICATION_NOT_FOUND.value,
            )
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "signal": "FAILED_TO_FETCH_NOTIFICATIONS",
                "message": f"Failed to fetch notifications: {str(e)}",
            },
        )


@notification_route.put(
    "/{notification_id}/mark_seen/",
    response_model=MarkReadResponse,
    status_code=status.HTTP_200_OK,
)
async def mark_read(
    notification_id: str,
    notification_model: NotificationModel = Depends(get_notification_model),
) -> MarkReadResponse:
    """
    Mark a specific notification as read (seen) by updating its `seen` field in the database.

    Args:
        notification_id (str): The unique identifier of the notification to mark as seen.
        notification_model (NotificationModel): Dependency-injected database model instance.

    Returns:
        MarkReadResponse: Object containing matched and modified counts.

    Raises:
        HTTPException(404): If the notification does not exist.
        HTTPException(500): If marking as read fails.
    """
    try:
        result = await notification_model.mark_as_seen(notification_id)

        if result.get("matched_count", 0) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail= ResponseSignal.NOTIFICATION_NOT_FOUND.value
            )

        return MarkReadResponse(
            notification_id= notification_id,
            modified_count=result["modified_count"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=  ResponseSignal.FAILED_TO_MARK_AS_READ.value
        )


@notification_route.post(
    "/",
    response_model=Notification,
    status_code=status.HTTP_201_CREATED,
)
async def send_notification(
    req: Notification,
    notification_model: NotificationModel = Depends(get_notification_model),
) -> Notification:
    """
    Create and send a new notification to a specific user.

    Args:
        req (SendNotificationRequest): Request body containing title, content, and user_id.
        notification_model (NotificationModel): Dependency-injected model instance for DB operations.

    Returns:
        Notification: The created notification document.

    Raises:
        HTTPException(400): If user_id is invalid.
        HTTPException(500): If the notification creation fails.
    """
    try:       
        result = await notification_model.create_notification(notification=req)
        req.id = str(result)
        return req

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Failed to send notification: {str(e)}",
        )
