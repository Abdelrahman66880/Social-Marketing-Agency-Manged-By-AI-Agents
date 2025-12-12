from typing import Optional, List, Annotated
from pydantic import Field, ConfigDict, BaseModel, BeforeValidator
from bson import ObjectId

# 1. Define PyObjectId exactly as in Schedule.py
PyObjectId = Annotated[str, BeforeValidator(str)]

class BusinessResource(BaseModel):
    name: str
    description: Optional[str] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)


class BuisnessInfo(BaseModel):
    # 2. Use PyObjectId for IDs
    id: Optional[PyObjectId] = Field(None, alias="_id")
    user_id: PyObjectId

    businessName: str
    field: str
    description: str = Field(
        ...,
        min_length=50,
        max_length=1000,
        description="A clear and representative description of the business (50-1000 characters)."
    )
    
    # Lists with defaults
    theme: List[str] = []
    longTermGoals: List[str] = []
    shortTermGoals: List[str] = []
    targetAudience: List[str] = []
    differentiators: List[str] = []
    businessKeyWords: List[str] = []
    
    # Optional nested models
    availableResources: Optional[List[BusinessResource]] = None

    # Facebook Integration
    facebook_page_id: Optional[str] = None
    facebook_page_access_token: Optional[str] = None

    # 3. ConfigDict for JSON encoding and examples
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={
            ObjectId: str,
        },
        json_schema_extra={
            "example": {
                "user_id": "66f82a12b5d92e61d7b23f99",
                "businessName": "EcoFriendly Tech",
                "field": "Technology",
                "description": "A leading provider of sustainable technology solutions for modern homes.",
                "theme": ["Green", "Modern"],
                "longTermGoals": ["Global expansion"],
                "shortTermGoals": ["Launch Q4 product"],
                "targetAudience": ["Eco-conscious homeowners"],
                "differentiators": ["100% Recyclable materials"],
                "businessKeyWords": ["Eco", "Tech", "Sustainable"],
                "facebook_page_id": "123456789",
                 # Token is usually not passed in creation example for security, but valid in schema
            }
        },
    )

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
