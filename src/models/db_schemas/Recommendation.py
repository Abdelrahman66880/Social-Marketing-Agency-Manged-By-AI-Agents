from typing import Optional, List
from pydantic import BaseModel, Field, ValidationError, model_validator
from bson import ObjectId
from datetime import datetime, timezone


class Recommendation(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")

    title: str = Field(..., min_length= 10, max_length=100, description="title of the recommendation filled by Ai agent")

    content: str= Field(..., min_length=10, description="AI prompt to make a recommendation")

    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    result: dict = Field(..., description="Recomendation reults")
    
    user_id: ObjectId

    class Config:
        arbitrary_types_allowed = True



    @classmethod
    def get_indexes(cls):
        return [
            {"key": [("user_id", 1)], "name": "user_index", "unique": False},
            {"key":[("createdAt", -1)], "name":"createdAt", "unique": False}
        ]
