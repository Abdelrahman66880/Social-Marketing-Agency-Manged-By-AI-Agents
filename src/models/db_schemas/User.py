from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator, validator, ConfigDict
from bson import ObjectId
from enum import Enum
from src.models.enums.UserEnums import AccountStatus


class User(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")

    accountStatus: AccountStatus = Field(..., description="User account status")

    username: str = Field(..., min_length=3, max_length=30, description="Unique username")

    hashPassword: str = Field(..., min_length=8, description="Hashed password string")

    email: EmailStr = Field(..., description="Unique user email")

    @field_validator('id', mode="after")
    def validate_post_id(cls, value):
        if not isinstance(value, ObjectId):
            raise ValueError("post_id must be a valid ObjectId")
        return value
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # ---------------------------
    # Validators
    # ---------------------------
    

    @field_validator("username", mode="after")
    @classmethod
    def validate_username(cls, v: str) -> str:
        import re
        if not re.match(r"^[a-zA-Z0-9 ]+$", v):
            raise ValueError("Username must only contain letters, numbers, and spaces")
        return v

    # ---------------------------
    # Index definitions
    # ---------------------------
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("username", 1)],
                "name": "username_index",
                "unique": True,
                "sparse": False,
            },
            {
                "key": [("email", 1)],
                "name": "email_index",
                "unique": True,
                "sparse": False,
            },
            {
                "key": [("accountStatus", 1)],
                "name": "account_status_index",
                "unique": False,
                "sparse": False,
            },
            {
                "key": [("facebookPageId", 1)],
                "name": "facebook_page_id_index",
                "unique": True,
                "sparse": True,
            },
        ]
    