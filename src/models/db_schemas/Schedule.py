from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from bson import ObjectId
from datetime import time
from models.enums.ScheduleEnums import DayOfWeek
from uuid import uuid4

class ScheduledPost(BaseModel):
    id: Optional[str] = Field(default=None, description="Unique ID, assigned by model")
    day_of_week: DayOfWeek
    time_of_day: time
    content: str= Field(..., min_length=10, max_length=1000, description="AI prompt to create a social media post")
    media_urls: Optional[List[str]] = Field(default_factory=list)

class ScheduledCompetitorAnalysis(BaseModel):
    id: Optional[str] = Field(default=None, description="Unique ID, assigned by model")
    day_of_week: DayOfWeek
    time_of_day: time
    analysis_focus: str = Field(..., min_length=10, max_length=1000,description="AI prompt specifying the competitor focus area for analysis" )
    keywords: Optional[List[str]] = Field(default_factory=list)


class interactionAnalysisDate(BaseModel):
    id: Optional[str] = Field(default=None, description="Unique ID, assigned by model")
    day_of_week: DayOfWeek
    time_of_day: time

class Schedule(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    posts: List[ScheduledPost] = Field(default_factory=list)
    competitor_analysis: List[ScheduledCompetitorAnalysis] = Field(default_factory=list)
    interaction_analysis_dates: List[interactionAnalysisDate] = Field(default_factory=list)
    user_id: ObjectId

    @field_validator('id', mode="after")
    def validate_post_id(cls, value):
        if not isinstance(value, ObjectId):
            raise ValueError("Schedule_id must be a valid ObjectId")
        return value
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="before")
    def no_duplicate_times(cls, values):
        def check_unique_times(items, name):
            seen = set()
            for item in items:
                key = (item.day_of_week, item.time_of_day)
                if key in seen:
                    raise ValueError(f"Duplicate {name} at {item.day_of_week} {item.time_of_day}")
                seen.add(key)

        check_unique_times(values.get("posts", []), "post")
        check_unique_times(values.get("competitor_analysis", []), "competitor analysis")
        check_unique_times(values.get("interaction_analysis_dates", []), "interaction analysis date")
        return values

    @classmethod
    def get_indexes(cls):
        return [
            {"key": [("user_id", 1)], "name": "user_index", "unique": True},
        ]
