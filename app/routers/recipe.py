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
    Form,
)
from app.database.models.recipe import Recipe
from app.database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession  # async creation of DB session
from sqlalchemy.future import select
from app.schemas import recipe_schemas
from app.auth import oauth2
import uuid, os, shutil


router = APIRouter(prefix="/recipes", tags=["recipes"])


# get all recipes


# get recipes with limit

# get recipe by id


# create recipe
"""
I would like for the API to work with file uploads
Because of that, we need to use form data in the backend and frontend
pydantic schemas would not work here, so we make an exception
"""


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=recipe_schemas.Recipe_Out
)
async def create_recipe(
    title: str = Form(...),
    ingredients: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(None),  # Optional image
    db: AsyncSession = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    # make a check for form data elements because we do not have a pydantic model here
    if not title or not ingredients or not description:
        raise HTTPException(
            status_code=404,
            detail="Title, description and ingredients fields are mandatory!",
        )
    # save the file if it is uploaded
    # Store the image locally in the project as a file if present
    image_path = None
    if image:
        extension = image.filename.split(".")[-1]
        unique_name = f"{uuid.uuid4()}.{extension}"
        upload_dir = "app/static/images"
        os.makedirs(upload_dir, exist_ok=True)
        file_location = os.path.join(upload_dir, unique_name)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_path = f"/static/images/{unique_name}"  # Or a public URL

    new_recipe = Recipe(
        title=title,
        ingredients=ingredients,
        description=description,
        image_path=image_path,
        owner_id=current_user.id,
    )
    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe)
    return new_recipe


# Update recipe

# Delete recipe

# Like recipe
