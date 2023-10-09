from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.database import Base

class Rooms(Base):
    __tablename__ = "rooms"

    id:          Mapped[int] = mapped_column(primary_key=True, nullable=False)
    hotel_id:    Mapped[int] = mapped_column(ForeignKey("hotels.id"), nullable=False)
    name:        Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str]
    price:       Mapped[int] = mapped_column(nullable=False)
    services:    Mapped[Optional[list[str]]] = mapped_column(JSON)
    quantity:    Mapped[int] = mapped_column(nullable=False)
    image_id:    Mapped[int]

    bookings: Mapped[list['Bookings']] = relationship(back_populates="room")
    hotel:    Mapped['Hotels'] = relationship(back_populates="rooms")

    def __str__(self) -> str:
        return f"Room {self.name}"
