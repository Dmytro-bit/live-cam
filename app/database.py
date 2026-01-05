from datetime import datetime, UTC

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()


class BaseModel(db.Model):
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(UTC)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC)
    )
