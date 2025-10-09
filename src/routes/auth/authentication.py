from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from src.models.UserModel import UserModel
from src.helpers.config import get_Settings

setting_object = get_Settings()
db_client = setting_object.MONGODB_URL
SECRET_KEY = setting_object.SECRET_KEY   
ALGORITHM = setting_object.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = setting_object.ACCESS_TOKEN_EXPIRE_DAYS

# tells FastAPI where the login route is
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db_client=db_client
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_model = await UserModel.create_instance(db_client)
    user = await user_model.get_user_by_id(user_id)
    if not user:
        raise credentials_exception
    return user
