from datetime import date

from sqlalchemy import Boolean, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPkMixin


class Season(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "seasons"

    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="ACTIVE")


class Competition(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "competitions"

    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str | None] = mapped_column(String)
    country: Mapped[str | None] = mapped_column(String)
    level: Mapped[str | None] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, nullable=False, default="ACTIVE")


class PlayerPosition(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "player_positions"

    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    position_group: Mapped[str | None] = mapped_column(String)
    display_order: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String, nullable=False, default="ACTIVE")
