from typing import Optional, List, Union
from pydantic import BaseModel, Field
from bson import ObjectId


class BusinessResource(BaseModel):
    type: str
    description: Optional[str] = None


class BuisnessInfo(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")

    theme: List[str] = []

    field: List[str] = []

    longTermGoals: List[str] = []

    shortTermGoals: List[str] = []

    businessName: str

    targetAudience: List[str] = []

    differentiators: List[str] = []

    availableResources: Optional[List[BusinessResource]] = None

    businessKeyWords: List[str] = []

    user_id: ObjectId

    description: str = Field(
        ...,
        min_length=50,
        max_length=1000,
        description="A clear and representative description of the business (50-1000 characters)."
    )

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("user_id", 1)],
                "name": "user_index",
                "unique": True,
            },
        ]



    
