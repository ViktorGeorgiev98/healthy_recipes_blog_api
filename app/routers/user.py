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
from app.schemas import user_schemas
from app.utils import password_hash


# create the user router
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
    hashed_password = await password_hash.hash(user.password)
    user.password = hashed_password
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
