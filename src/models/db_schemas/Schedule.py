from typing import Optional, List, Annotated
from datetime import datetime
from uuid import uuid4
from bson import ObjectId
from pydantic import (
    BaseModel,
    Field,
    model_validator,
    ConfigDict,
    BeforeValidator,
)

PyObjectId = Annotated[str, BeforeValidator(str)]
class ScheduleBase(BaseModel):
    """Base model providing shared configuration for all schedule items."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            ObjectId: str,
        },
    )


class ScheduledPost(ScheduleBase):
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
    date: datetime
    content: str = Field(..., min_length=10, max_length=1000)
    media_urls: List[str] = Field(default_factory=list)


class ScheduledCompetitorAnalysis(ScheduleBase):
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
    date: datetime
    analysis_focus: str = Field(..., min_length=10, max_length=1000)
    keywords: List[str] = Field(default_factory=list)


class InteractionAnalysisDate(ScheduleBase):
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
    date: datetime


class Schedule(ScheduleBase):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    user_id: PyObjectId
    posts: List[ScheduledPost] = Field(default_factory=list)
    competitor_analysis: List[ScheduledCompetitorAnalysis] = Field(default_factory=list)
    interaction_analysis_dates: List[InteractionAnalysisDate] = Field(default_factory=list)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            ObjectId: str,
        },
        json_schema_extra={
            "example": {
                "user_id": "66f82a12b5d92e61d7b23f99",
                "posts": [
                    {
                        "id": "post_1",
                        "date": "2025-10-10T09:00:00",
                        "content": "Generate an AI post about sustainable tech trends.",
                        "media_urls": [
                            "https://cdn.example.com/images/post1.png",
                            "https://cdn.example.com/images/post1_banner.jpg",
                        ],
                    }
                ],
                "competitor_analysis": [
                    {
                        "id": "comp_1",
                        "date": "2025-10-10T10:30:00",
                        "analysis_focus": "Analyze engagement rates of top 3 competitors in healthcare AI.",
                        "keywords": ["AI", "healthcare", "engagement", "competitors"],
                    }
                ],
                "interaction_analysis_dates": [
                    {"id": "int_1", "date": "2025-10-10T20:00:00"}
                ],
            }
        },
    )

    @model_validator(mode="before")
    def no_duplicate_times(cls, values):
        """Ensure no duplicate dates across submodels."""
        def check_unique_times(items: list, name: str):
            seen = set()
            for item in items:
                if not isinstance(item, dict):
                    continue
                key = item.get("date")
                if key in seen:
                    raise ValueError(f"Duplicate {name} date: {key}")
                seen.add(key)

        check_unique_times(values.get("posts", []), "post")
        check_unique_times(values.get("competitor_analysis", []), "competitor analysis")
        check_unique_times(values.get("interaction_analysis_dates", []), "interaction analysis date")

        return values

    @classmethod
    def get_indexes(cls):
        return [{"key": [("user_id", 1)], "name": "user_index", "unique": True}]
