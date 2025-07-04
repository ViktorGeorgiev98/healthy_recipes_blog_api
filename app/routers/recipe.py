from fastapi import (
    FastAPI,
    Response,
    status,
    staticfiles,
    HTTPException,
    Depends,
    APIRouter,
)
from app.database.models.recipe import Recipe
from app.database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession  # async creation of DB session
from sqlalchemy.future import select
from app.schemas import recipe_schemas
from app.auth import oauth2

router = APIRouter(prefix="/recipes", tags=["recipes"])
