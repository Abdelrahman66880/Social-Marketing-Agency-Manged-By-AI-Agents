from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class PageInfoSchema(BaseModel):
    id: Optional[str] = None         #READ only
    name: Optional[str] = None       #READ only
    category: Optional[str] = None
    about: Optional[str] = None
    description: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    category_list: Optional[List[dict]] = None

class PostUploadSchema(BaseModel):
    message: Optional[str] = Field(None, description="Text content or caption for the post")
    image_url: Optional[str] = Field(None, description="URL of the image to upload")
    video_url: Optional[str] = Field(None, description="URL of the video to upload")
