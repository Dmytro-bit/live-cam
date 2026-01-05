from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database import BaseModel


class User(BaseModel):
    username: Mapped[str] = mapped_column(unique=True)
    is_active: Mapped[Boolean] = mapped_column(default=True)
