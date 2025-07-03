from pydantic import BaseModel, EmailStr, conint, validator
from datetime import datetime
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class Token_Data(BaseModel):
    id: Optional[int] = None
