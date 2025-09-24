from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from enum import Enum
from ..enums.UserEnums import AccountStatus

class User(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")

    accountStatus: AccountStatus = Field(..., description="User account status")

    username: str = Field(..., min_length=3, max_length=30, description="Unique username")

    hashPassword: str = Field(..., description="Hashed password string")

    email: EmailStr = Field(..., description="Unique user email")

    facebookPageId: Optional[str] = Field(None, description="Facebook Page ID linked via Meta Graph API")
    
    class Config:
        arbitary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("username", 1)],
                "name": "username_index",
                "unique": True,
                "sparse": False
            },
            {
                "key": [("email", 1)],
                "name": "email_index",
                "unique": True,
                "sparse": False

            },
            {
                "key": [("accountStatus", 1)],
                "name": "account_status_index",
                "unique": False,
                "sparse": False
            },
            {
                "key": [("facebookPageId", 1)],
                "name": "facebook_page_id_index",
                "unique": True,
                "sparse": True
            },
        ]
