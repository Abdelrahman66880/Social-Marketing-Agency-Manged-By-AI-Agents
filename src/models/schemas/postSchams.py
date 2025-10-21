from pydantic import BaseModel, EmailStr
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

class PostUpdateSchema(BaseModel):
    message: Optional[str] = None
    link: Optional[str] = None
    
class PostUploadSchema(BaseModel):
    message: str
