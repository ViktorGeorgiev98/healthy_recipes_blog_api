from fastapi import (
    FastAPI,
    Response,
    status,
    staticfiles,
    HTTPException,
    Depends,
    APIRouter,
    UploadFile,
    File,
)
from app.database.models.recipe import Recipe
from app.database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession  # async creation of DB session
from sqlalchemy.future import select
from app.schemas import recipe_schemas
from app.auth import oauth2

router = APIRouter(prefix="/recipes", tags=["recipes"])


# get all recipes


# get recipes with limit

# get recipe by id


# create recipe
@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=recipe_schemas.Recipe_Out
)
def create_recipe(
    recipe: recipe_schemas.Recipe_Create,
    db: AsyncSession = Depends(get_db),
    current_user=oauth2.get_current_user,
):
    pass


# update recipe

# delete recipe
