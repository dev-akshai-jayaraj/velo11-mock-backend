import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPkMixin


class HomeClub(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "home_clubs"

    name: Mapped[str] = mapped_column(String, nullable=False)
    short_name: Mapped[str | None] = mapped_column(String)
    logo_url: Mapped[str | None] = mapped_column(String)
    country: Mapped[str | None] = mapped_column(String)
    timezone: Mapped[str | None] = mapped_column(String)
    primary_color: Mapped[str | None] = mapped_column(String)
    secondary_color: Mapped[str | None] = mapped_column(String)
    home_venue_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("venues.id")
    )
    status: Mapped[str] = mapped_column(String, nullable=False, default="ACTIVE")


class Venue(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "venues"

    name: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[str | None] = mapped_column(String)
    city: Mapped[str | None] = mapped_column(String)
    address: Mapped[str | None] = mapped_column(Text)
    surface_type: Mapped[str | None] = mapped_column(String)
    capacity: Mapped[int | None] = mapped_column(Integer)
    is_home_venue: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="ACTIVE")


class OwnTeam(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "own_teams"

    home_club_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("home_clubs.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    short_name: Mapped[str | None] = mapped_column(String)
    team_type: Mapped[str | None] = mapped_column(String)
    gender: Mapped[str | None] = mapped_column(String)
    age_group: Mapped[str | None] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, nullable=False, default="ACTIVE")
