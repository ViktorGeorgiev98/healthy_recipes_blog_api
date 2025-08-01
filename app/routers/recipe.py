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
from app.database.models.like import Like
from app.database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession  # async creation of DB session
from sqlalchemy.future import select
from sqlalchemy import or_, desc
from app.schemas import recipe_schemas
from app.auth import oauth2
import uuid, os, shutil


router = APIRouter(prefix="/recipes", tags=["recipes"])


# get all recipes or get recipes with limit and offset. Limit is 100 by default
@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=list[recipe_schemas.Recipe_Out]
)
async def get_all_recipes(
    db: AsyncSession = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
    order_by: str = "created_at",
    search: str | None = None,  # New search query parameter
):
    """
    Get all recipes with optional search.

    - **limit**: Max number of recipes to return (default: 100)
    - **offset**: How many recipes to skip (for pagination)
    - **order_by**: Field to order by (`created_at` or `likes`)
    - **search**: Optional search term to filter recipes by title, description, or ingredients.
    """

    query = select(Recipe)

    if search:
        query = query.where(
            or_(
                Recipe.title.ilike(f"%{search}%"),
                Recipe.description.ilike(f"%{search}%"),
                Recipe.ingredients.ilike(f"%{search}%"),
            )
        )

    query = query.order_by(desc(order_by)).limit(limit).offset(offset)

    result = await db.execute(query)
    recipes = result.scalars().all()
    return recipes


# get recipe by id
@router.get(
    "/{id}", status_code=status.HTTP_200_OK, response_model=recipe_schemas.Recipe_Out
)
async def get_recipe_by_id(id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a recipe by its ID.

    This endpoint retrieves a specific recipe from the database using its unique identifier.
    If the recipe is not found, it raises a 404 HTTP exception.

    Parameters:
    - **id**: The unique identifier of the recipe to retrieve.
    - **db**: SQLAlchemy asynchronous session (injected via dependency).

    Returns:
    - The recipe as a `Recipe_Out` schema.

    Raises:
    - **HTTPException 404** if the recipe with the specified ID does not exist.
    """
    result = await db.execute(select(Recipe).where(Recipe.id == id))
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


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
@router.put(
    "/{id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=recipe_schemas.Recipe_Out,
)
async def update_recipe(
    id: int,
    title: str = Form(...),
    ingredients: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(None),  # Optional image
    db: AsyncSession = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """
    Update an existing recipe by its ID.

    This endpoint allows you to modify the title, ingredients, description, and optionally upload a new image for the recipe.

    Parameters:
    - **id**: The unique identifier of the recipe to update.
    - **title**: The new title of the recipe (required).
    - **ingredients**: The new ingredients used in the recipe (required).
    - **description**: The updated description of the recipe (required).
    - **image**: Optional new image file upload (JPG/PNG/etc.).
    - **db**: SQLAlchemy asynchronous session (injected via dependency).
    - **current_user**: The currently authenticated user (injected via dependency).

    Returns:
    - The updated recipe as a `Recipe_Out` schema.

    Raises:
    - **HTTPException 404** if the recipe with the specified ID does not exist.
    """
    if not title or not ingredients or not description:
        raise HTTPException(
            status_code=404,
            detail="Title, description and ingredients fields are mandatory!",
        )

    result = await db.execute(select(Recipe).where(Recipe.id == id))
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if recipe.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="You do not have permission to update this recipe"
        )
    print(recipe.owner_id, current_user.id)

    # Update fields
    recipe.title = title
    recipe.ingredients = ingredients
    recipe.description = description

    # Handle optional image upload
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
        recipe.image_path = f"/static/images/{unique_name}"

    await db.commit()
    await db.refresh(recipe)
    result = await db.execute(select(Recipe).where(Recipe.id == id))
    return result.scalars().one_or_none()


# Delete recipe
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """
    Delete a recipe by its ID.

    This endpoint allows you to delete a specific recipe from the database.

    Parameters:
    - **id**: The unique identifier of the recipe to delete.
    - **db**: SQLAlchemy asynchronous session (injected via dependency).
    - **current_user**: The currently authenticated user (injected via dependency).

    Returns:
    - No content (204) if the deletion is successful.

    Raises:
    - **HTTPException 404** if the recipe with the specified ID does not exist.
    - **HTTPException 403** if the user does not have permission to delete the recipe.
    """
    result = await db.execute(select(Recipe).where(Recipe.id == id))
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if recipe.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="You do not have permission to delete this recipe"
        )

    await db.delete(recipe)
    await db.commit()


# Like recipe
@router.post(
    "/{id}/like",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=recipe_schemas.Recipe_Out,
)
async def like_recipe(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """
    Like a recipe by its ID.

    This endpoint allows a user to like a specific recipe. It increments the like count for the recipe
    and returns the updated recipe information.

    Parameters:
    - **id**: The unique identifier of the recipe to like.
    - **db**: SQLAlchemy asynchronous session (injected via dependency).
    - **current_user**: The currently authenticated user (injected via dependency).

    Returns:
    - The updated recipe as a `Recipe_Out` schema.

    Raises:
    - **HTTPException 404** if the recipe with the specified ID does not exist.
    """
    result = await db.execute(select(Recipe).where(Recipe.id == id))
    recipe = result.scalar_one_or_none()

    result = await db.execute(select(Recipe).where(Recipe.id == id))
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if current_user.id == recipe.owner_id:
        raise HTTPException(status_code=403, detail="You cannot like your own recipe")
    result_likes = await db.execute(
        select(Like).where(Like.user_id == current_user.id, Like.recipe_id == id)
    )
    existing_like = result_likes.scalar_one_or_none()
    if existing_like:
        raise HTTPException(
            status_code=400, detail="You have already liked this recipe"
        )
    new_like = Like(user_id=current_user.id, recipe_id=id)
    db.add(new_like)
    await db.commit()
    await db.refresh(new_like)
    recipe.likes += 1  # Increment the like count
    await db.commit()
    await db.refresh(recipe)
    return recipe


# Remove like from recipe
@router.delete(
    "/{id}/like",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=recipe_schemas.Recipe_Out,
)
async def remove_like_from_recipe(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """
    Remove a like from a recipe by its ID.

    This endpoint allows a user to remove their like from a specific recipe.

    Parameters:
    - **id**: The unique identifier of the recipe to unlike.
    - **db**: SQLAlchemy asynchronous session (injected via dependency).
    - **current_user**: The currently authenticated user (injected via dependency).

    Returns:
    - No content (204) if the unlike operation is successful.

    Raises:
    - **HTTPException 404** if the recipe with the specified ID does not exist.
    - **HTTPException 403** if the user does not have permission to unlike the recipe.
    """
    result = await db.execute(select(Recipe).where(Recipe.id == id))
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if recipe.owner_id == current_user.id:
        raise HTTPException(
            status_code=403, detail="You cannot remove like from your own recipe"
        )

    result_likes = await db.execute(
        select(Like).where(Like.user_id == current_user.id, Like.recipe_id == id)
    )
    existing_like = result_likes.scalar_one_or_none()

    if not existing_like:
        raise HTTPException(status_code=404, detail="You have not liked this recipe")

    await db.delete(existing_like)
    await db.commit()

    recipe.likes -= 1  # Decrement the like count
    await db.commit()
    return recipe
