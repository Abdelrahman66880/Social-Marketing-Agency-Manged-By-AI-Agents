from pydantic import BaseModel, EmailStr
from typing import Optional

class PageUpdateSchema(BaseModel):
    about: Optional[str] = None
    description: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
