from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import BaseModel, UpdateModel


class Device(BaseModel, UpdateModel):
    certificate_string: Mapped[str] = mapped_column(String(255), nullable=False)
    chanel_name: Mapped[str] = mapped_column(String(255), nullable=False)
