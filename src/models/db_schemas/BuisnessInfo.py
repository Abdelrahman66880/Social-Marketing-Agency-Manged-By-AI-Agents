from typing import Optional, List, Union
from pydantic import Field, ConfigDict, field_validator
from bson import ObjectId
from pydantic import BaseModel


class BusinessResource(BaseModel):
    name: str
    description: Optional[str] = None


class BuisnessInfo(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")

    theme: List[str] = []

    field: str

    longTermGoals: List[str] = []

    shortTermGoals: List[str] = []

    businessName: str

    targetAudience: List[str] = []

    differentiators: List[str] = []

    availableResources: Optional[List[BusinessResource]] = None

    businessKeyWords: List[str] = []

    facebook_page_id: Optional[str] = None
    facebook_page_access_token: Optional[str] = None

    user_id: ObjectId

    description: str = Field(
        ...,
        min_length=50,
        max_length=1000,
        description="A clear and representative description of the business (50-1000 characters)."
    )

    @field_validator('id', mode="after")
    def validate_post_id(cls, value):
        if not isinstance(value, ObjectId):
            raise ValueError("BuisnessInfo_id must be a valid ObjectId")
        return value
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("user_id", 1)],
                "name": "user_index",
                "unique": True,
            },
            {
                "key": [("facebook_page_id", 1)],
                "name": "facebook_page_id_index",
                "unique": True,
                "sparse": True,
            },
        ]



    
