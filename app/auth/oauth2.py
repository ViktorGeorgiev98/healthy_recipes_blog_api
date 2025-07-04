from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.schemas.token import Token_Data
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.database.models.user import User
import os
from app.config.config import settings
from sqlalchemy.future import select


# initiate the oauth2 scheme using the password bearer to correspond to url with 'login'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# secret key
SECRET_KEY = settings.secret_key

# algorithm to encode the JWT
ALGORITHM = settings.algorithm

# expiration date for the token in minutes
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    # copy the data as to not have bugs
    to_encode = data.copy()
    # set the expiration date
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # add the expiration to the token object
    to_encode.update({"exp": expire})
    # create (encode) the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    # return the encoded token
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        # get the payload by decoding the token by using the token, secret key and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = Token_Data(id=id)
    except JWTError:
        raise credentials_exception
    return token_data


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=404,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = verify_access_token(token, credentials_exception=credentials_exception)
    query = await db.execute(select(User).where(User.id == token.id))
    user = query.scalars().first()
    return user
