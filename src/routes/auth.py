from fastapi import FastAPI, Depends, status, HTTPException, APIRouter
from models.UserModel import UserModel
from jose import jwt, JWTError
from passlib.context import CryptContext
from helpers.config import get_Settings
from passlib.context import CryptContext
from models.db_schemas.User import User
from models.enums.ResponseSignal import ResponseSignal
from models.enums.UserEnums import AccountStatus
from fastapi.responses import JSONResponse
import bcrypt

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

@auth_router.post("/register")
async def register_user(user_data: dict, db_client=Depends(get_Settings().MONGODB_URL)):
    user_model = await UserModel.create_instance(db_client=db_client)
    
    if await user_model.exists_by_email(user_data["email"]):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.ERROR_USER_IS_ALREADY_EXIST.value
            }
        )
        
    hashed_password = bcrypt.hashpw(user_data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    new_user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashPassword=hashed_password,
        accountStatus=AccountStatus.ACTIVE.value
    )
    
    await user_model.create_user(user=new_user)
    return JSONResponse(
        content={
            "signal": ResponseSignal.USER_REGISTERED_SUCCESSFULLY.value
        }
    )
