from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.config import settings


# Create the database URL
# local
# DATABASE_URL = f"postgresql+asyncpg://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
# railway
if settings.database_url:
    DATABASE_URL = settings.database_url
else:
    DATABASE_URL = DATABASE_URL = f"postgresql+asyncpg://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"



# Create the engine
engine = create_async_engine(DATABASE_URL, echo=True)

# create the session
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# create the base class
Base = declarative_base()


# function to create the tables upon startup of the application
async def create_db_and_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        print("DB created and tables initialized")


# function to get the database and be able to make queries
async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"Issue with getting DB: {e}")
        raise
    finally:
        await db.close()
