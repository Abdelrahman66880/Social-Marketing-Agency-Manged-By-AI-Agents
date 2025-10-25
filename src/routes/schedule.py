from fastapi import APIRouter, status, Request, Depends, HTTPException
from src.models.db_schemas.Schedule import Schedule
from src.models.ScheduleModel import ScheduleModel
from fastapi.encoders import jsonable_encoder

schedule_router = APIRouter(prefix="/schedule", tags=["Schedule"])

async def get_schedule_model(request: Request) -> ScheduleModel:
    """Dependency to get a ScheduleModel instance."""
    db_client = request.app.db_client
    return await ScheduleModel.create_instance(db_client)


@schedule_router.get("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=Schedule)
async def get_schedule(user_id: str, schedule_model: ScheduleModel = Depends(get_schedule_model)) -> Schedule:
    """
    Get a user's schedule by user_id.

    Args:
        user_id (str): User's ObjectId as string.
    Returns:
        Schedule: The user's schedule.
    Raises:
        HTTPException(404): If not found.
    """
    try :
        result = await schedule_model.get_by_user_id(user_id=user_id)
        if not result:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return result
    except Exception as e:

        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Failed to get schedule for the following reason: {str(e)}",
        )


@schedule_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Schedule)
async def set_schedule(schedule: Schedule, schedule_model: ScheduleModel = Depends(get_schedule_model)) -> Schedule:
    try:
        result = await schedule_model.create_schedule(schedule=schedule)
        schedule.id = str(result)
        return jsonable_encoder(schedule)
    except Exception as e:
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create schedule for the following reason: {str(e)}"
        )




@schedule_router.put("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=Schedule)
async def edit_schedule(
    new_schedule: Schedule,
    user_id: str,
    schedule_model: ScheduleModel = Depends(get_schedule_model)
) -> Schedule:
    """
    Replace an existing schedule.

    Args:
        new_schedule (Schedule): Updated schedule data.
        user_id (str): User's ObjectId as string.
    Returns:
        Schedule: Updated schedule.
    Raises:
        HTTPException(404): If not found.
        HTTPException(400): If no changes applied.
    """
    try:
        result = await schedule_model.replace_schedule_by_user_id(user_id=user_id, new_schedule=new_schedule)
        if result["matched_count"] == 0:
            raise HTTPException(status_code=404, detail="schedule not found")
        
        if result["modified_count"] == 0:
            raise HTTPException(status_code=400, detail="No changes were applied")

        new_doc = new_schedule.model_dump(by_alias=True, exclude_unset=True)
        new_doc["_id"] = result["_id"]

        return new_doc
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Failed to edit schedule for the following reasong: {str(e)}"
        )