from pydantic_settings import BaseSettings

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
    pgdata: str
    pgdatabase: str
    pghost: str
    pgpassword: str
    pgport: str
    pguser: str
    postgres_db: str
    postgres_password: str
    database_url: str
    postgres_user: str
    database_public_url: str

    class Config:
        env_file = ".env"


settings = Settings()
