from app.database.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship


class Like(Base):
    __tablename__ = "likes"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    recipe_id = Column(
        Integer, ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True
    )
