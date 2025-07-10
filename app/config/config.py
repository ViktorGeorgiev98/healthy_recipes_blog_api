from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import asyncpg

"""
    This class is used to store the settings for the application.
    The environment variables are stored in the .env file.
    The settings are loaded from the .env file.
    The settings are used to configure the application.
    The settings are used to configure the database.
    The settings are used to configure the authentication.
    At the end of the file we initialize the settings object and we can use it in the application.
"""

# local .env file
# class Settings(BaseSettings):
#     database_hostname: str
#     database_port: str
#     database_password: str
#     database_name: str
#     database_username: str
#     secret_key: str
#     algorithm: str
#     access_token_expire_minutes: int
#     database_url: str

#     class Config:
#         env_file = ".env"

# railway
class Settings(BaseSettings):
    # Railway
    database_url: Optional[str] = Field(default=None)

    # Local (used only if database_url is None)
    database_hostname: Optional[str] = Field(default=None)
    database_port: Optional[str] = Field(default="5432")
    database_password: Optional[str] = Field(default=None)
    database_name: Optional[str] = Field(default=None)
    database_username: Optional[str] = Field(default=None)

    # Auth settings
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()
