from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timezone

class UserModel(BaseModel):
    email: EmailStr
    username: str
    google_id: Optional[str] = None
    profile_picture: Optional[str] = None
    workspace: Optional[str] = None
    access_token: str
    refresh_token: str
    is_new: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
