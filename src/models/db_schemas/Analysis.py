from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime

class Analysis(BaseModel):
    id : Optional[ObjectId] = Field(None, alias="_id")
    post_id: ObjectId
    analysisType: str
    createdAt: datetime
    
    @field_validator('id', mode="after")
    def validate_post_id(cls, value):
        if not isinstance(value, ObjectId):
            raise ValueError("analysis_id must be a valid ObjectId")
        return value
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("analysis_id", 1)],
                "name": "analysis_index",
                "unique": False,
            },
        ]