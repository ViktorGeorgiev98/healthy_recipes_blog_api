from app.database.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    ingredients = Column(String, nullable=False)
    description = Column(String, nullable=False)
    image_path = Column(String, nullable=True)
    likes = Column(Integer, nullable=False, server_default=text("0"))
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default="now()"
    )
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    owner = relationship("User")
