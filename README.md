# 🥗 Healthy Recipes Blog API

A FastAPI-based RESTful API for managing healthy recipes with authentication, recipe CRUD, and like functionality. Built using modern async Python stack with PostgreSQL and deployed on Railway.

Main URL => [https://healthyrecipesblogapi-production.up.railway.app/](https://healthy-recipes-blog-api.onrender.com/)

Please go to [https://healthyrecipesblogapi-production.up.railway.app](https://healthy-recipes-blog-api.onrender.com/docs) for full documentation and requirements for the usage of the requests

---

## 🚀 Features

- 🔐 **User Authentication**
  - Registration with **secure password validation**:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one symbol
  - JWT-based login and protected routes

- 📋 **Recipe Management**
  - CRUD operations for recipes
  - Recipes linked to their authors

- ❤️ **Like System**
  - Authenticated users can like and unlike recipes

- 🗄️ **Database**
  - PostgreSQL with SQLAlchemy ORM (`asyncpg` support)
  - Alembic for migrations


---

## 📦 Requirements

- Python 3.11+
- PostgreSQL

Install dependencies:

```bash
pip install -r requirements.txt


requirements.txt includes:
fastapi
uvicorn[standard]
sqlalchemy
asyncpg
alembic
pydantic
python-jose
passlib[bcrypt]
python-dotenv
python-multipart
httpx
pytest
pytest-asyncio
pytest-cov
gunicorn
pydantic_settings
pydantic[email]
psycopg2


## 📁 Project Structure

app/
├── main.py                # FastAPI app entry point
├── models/                # SQLAlchemy models
├── schemas/               # Pydantic schemas
├── routes/                # API routers
├── database/              # DB session, config, migrations
├── auth/                  # JWT & password utilities
├── tests/                 # Test suite
.env                       # Environment config
alembic/                   # DB migration scripts


## 🛠️ Configuration
Environment variables should be stored in a .env file:


## 🔐 Auth Flow
1. Register at POST /register

2. Login at POST /login to receive a JWT

3. Include your token in the Authorization header for protected endpoints:
Authorization: Bearer <your_token>

## 🖥️ Run Locally
Start the app in development:
uvicorn app.main:app --reload


## 🌐 API Overview
| Method | Endpoint        | Description              |
| ------ | --------------- | ------------------------ |
| POST   | `/register`     | Register new user        |
| POST   | `/login`        | Login and get JWT        |
| GET    | `/recipes/`     | Get all recipes          |
| POST   | `/recipes/`     | Create new recipe (auth) |
| PUT    | `/recipes/{id}` | Update recipe (auth)     |
| DELETE | `/recipes/{id}` | Delete recipe (auth)     |
| POST   | `/like/{id}`    | Like a recipe (auth)     |
| DELETE | `/like/{id}`    | Remove like from recipe  |


## Deployment
Deployed on Railway.

## 📄 License
MIT License © [ViktorGeorgiev98] 

