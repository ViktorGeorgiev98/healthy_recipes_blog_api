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
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import oauth2

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
async def register(
    user_register: user_schemas.UserCreate, db: AsyncSession = Depends(get_db)
):
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
    query = await db.execute(select(User).where(User.email == user_register.email))
    user = query.scalars().first()
    if user:
        raise HTTPException(
            status_code=404,
            detail=f"User with email {user_register.email} already exists!",
        )
    hashed_password = password_hash.hash(user_register.password)
    user_register.password = hashed_password
    new_user = User(**user_register.dict())
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
    query = await db.execute(select(User).where(User.id == id))
    user = query.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id {id} not found!")
    return user


# Login
# test password => 12345!aA
@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    user_login: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    query = await db.execute(select(User).where(User.email == user_login.username))
    user = query.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="Invalid credentials!")
    # need to compare the plain password the current user has written with the hashed password
    # of the user found in the DB with the provided email
    # That is very important, otherwise you get bugs
    password_is_correct = password_hash.verify_password(
        user_login.password, user.password
    )
    if not password_is_correct:
        raise HTTPException(status_code=404, detail="Invalid credentials!")

    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "access_token": access_token,
            "token_type": "bearer",
        }
    }
