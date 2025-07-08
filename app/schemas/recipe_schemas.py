from pydantic import BaseModel, EmailStr, conint, validator
from typing import Optional
from datetime import datetime


class Recipe_Create(BaseModel):
    title: str
    ingredients: str
    description: str


class Recipe_Out(BaseModel):
    id: int
    title: str
    ingredients: str
    image_path: Optional[str] = None
    likes: int
    created_at: datetime
    description: str
    owner_id: int
