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
from sqlalchemy.ext.asyncio import AsyncSession  # async creation of DB session
from sqlalchemy.future import select
from app.schemas import user_schemas
from app.utils import password_hash


"""
Create the router from the API router imported from fastapi
make a prefix /users => that means all routes will start from there per default
tags is just to make the fastapi documentation better structured
"""
router = APIRouter(
    prefix="/users", tags=["Users"]  # for better structure of fast api documentation
)


# Register user
@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=user_schemas.UserOut,
)
async def register(user: user_schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.

    - Hashes the user's password using bcrypt for secure storage.
    - Creates a new user record in the database with the provided email and hashed password.
    - Commits the new user to the database and returns the created user (excluding the password).

    Args:
        user (UserCreate): The user registration data (email and password).
        db (AsyncSession): The asynchronous database session (provided by dependency injection).

    Returns:
        UserOut: The created user, including id, email, and creation timestamp.

    Raises:
        HTTPException: If the user cannot be created (e.g., due to a database error or duplicate email).
    """
    hashed_password = await password_hash.hash(user.password)
    user.password = hashed_password
    new_user = User(**user.dict())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


# get user
@router.get(
    "/{id}", status_code=status.HTTP_200_OK, response_model=user_schemas.UserOut
)
async def get_user_by_id(id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a user by their unique ID.

    - Queries the database for a user with the specified ID.
    - Returns the user if found, or raises a 404 error if not found.

    Args:
        id (int): The unique identifier of the user to retrieve.
        db (AsyncSession): The asynchronous database session (provided by dependency injection).

    Returns:
        UserOut: The user with the specified ID, including id, email, and creation timestamp.

    Raises:
        HTTPException: If no user with the given ID exists (404 Not Found).
    """
    result = await db.execute(select(User).where(User.id == id))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id {id} not found!")
    return user
