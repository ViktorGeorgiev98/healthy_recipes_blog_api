from fastapi import (
    FastAPI,
    Response,
    status,
    staticfiles,
    HTTPException,
    Depends,
    APIRouter,
)
from app.database.models.user import User
from app.database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


# create the user router
router = APIRouter(
    prefix="/users", tags=["Users"]  # for better structure of fast api documentation
)
