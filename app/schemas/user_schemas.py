from pydantic import BaseModel, EmailStr, conint, validator
from datetime import datetime
from typing import Optional
import re

"""
User related pydantic schemas
Each different schema defines what is mandatory when using an instance of that class
Also, it defines what information is returned from a request to the db
useful to always make sure we send all required data, but to not receive passwords as response
"""


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    # function to validate password
    @validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long!")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter!")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter!")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit!")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one symbol!")
        return value


class UserOut(BaseModel):
    # we must not send back the password in the response even if it is hashed
    email: EmailStr
    id: int
    created_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str
