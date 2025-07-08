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
@router.get("/", status_code=status.HTTP_200_OK, response_model=list[recipe_schemas.Recipe_Out]) # must be a list of recipes, otherwise it will not work
async def get_all_recipes(db: AsyncSession = Depends(get_db)):
    """
    Get all recipes from the database.
    """
    result = await db.execute(select(Recipe))
    recipes = result.scalars().all()
    return recipes

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
    """
    Creates a new recipe in the database.

    This endpoint handles multipart/form-data requests to allow image uploads along with other
    form fields. It saves the image to the local filesystem (under `app/static/images/`) and stores
    a public-facing path to it in the database.

    Parameters:
    - **title**: The title of the recipe (required).
    - **ingredients**: A string describing the ingredients used (required).
    - **description**: Detailed steps or notes for the recipe (required).
    - **image**: Optional image file upload (JPG/PNG/etc.).
    - **db**: SQLAlchemy asynchronous session (injected via dependency).
    - **current_user**: The currently authenticated user (injected via dependency).

    Returns:
    - The newly created recipe as a `Recipe_Out` schema.

    Raises:
    - **HTTPException 404** if required fields are missing.
    """
    if not title or not ingredients or not description:
        raise HTTPException(
            status_code=404,
            detail="Title, description and ingredients fields are mandatory!",
        )
    # Handle optional image upload
    image_path = None
    if image:
        extension = image.filename.split(".")[-1]
        unique_name = f"{uuid.uuid4()}.{extension}"
        upload_dir = "app/static/images"
        os.makedirs(upload_dir, exist_ok=True)
        file_location = os.path.join(upload_dir, unique_name)
        
        # Save uploaded file to the specified location
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
            
        # Relative path to be saved in the database (publicly accessible if static is mounted)
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
