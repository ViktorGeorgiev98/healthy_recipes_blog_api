from passlib.context import CryptContext


# set up the password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str) -> str:
    """
    Hash a password using the configured hashing context.

    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password) -> bool:
    """
    return the boolean result of bcrypt comparing the hashed password with the plain one
    if they are equal, the user wrote the correct password
    """
    return pwd_context.verify(plain_password, hashed_password)
