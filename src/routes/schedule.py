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
    result = await schedule_model.get_by_user_id(user_id=user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return result


@schedule_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Schedule)
async def set_schedule(schedule: Schedule, schedule_model: ScheduleModel = Depends(get_schedule_model)) -> Schedule:
    result = await schedule_model.create_schedule(schedule=schedule)
    schedule.id = str(result)
    return jsonable_encoder(schedule)




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
    # Ensure the user_id in the body matches the path for consistency
    new_schedule.user_id = user_id
    
    result = await schedule_model.replace_schedule_by_user_id(user_id=user_id, new_schedule=new_schedule)
    
    # We no longer raise 404 because we are upserting (creating if not found)
    
    new_doc = new_schedule.model_dump(by_alias=True, exclude_unset=True)
    new_doc["_id"] = str(result["_id"])

    return new_doc