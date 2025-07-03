from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.config import settings
from app.database import database
from app.database.models.like import Like
from app.database.models.recipe import Recipe
from app.database.models.user import User
from app.routers import user

# initialize the fastapi instance and configure middleware for cors
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all hosts/urls to access the api
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


# create db and tables if required
@app.on_event("startup")
async def on_startup():
    await database.create_db_and_tables()


# make first default route
@app.get("/")
async def root():
    return {"message": "This is the healthy recipes blog API"}


app.include_router(user.router)
