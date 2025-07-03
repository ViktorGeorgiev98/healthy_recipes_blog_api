from passlib.context import CryptContext


# set up the password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def hash(password: str) -> str:
    """
    Hash a password using the configured hashing context.

    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
