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


class Settings(BaseSettings):
    database_url: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()
