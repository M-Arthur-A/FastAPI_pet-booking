from sqlalchemy import JSON, ForeignKey, Date, Computed
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime

from app.database import Base


class Bookings(Base):
    __tablename__ = "bookings"

    id:         Mapped[int] = mapped_column(primary_key=True)
    room_id:    Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    user_id:    Mapped[int] = mapped_column(ForeignKey("users.id"))
    date_from:  Mapped[datetime] = mapped_column(Date, nullable=False)
    date_to:    Mapped[datetime] = mapped_column(Date, nullable=False)
    price:      Mapped[int] = mapped_column(nullable=False)
    total_cost: Mapped[int] = mapped_column(Computed("(date_to - date_from) * price"))
    total_days: Mapped[int] = mapped_column(Computed("date_to - date_from"))

    user: Mapped['Users'] = relationship(back_populates="bookings")
    room: Mapped['Rooms'] = relationship(back_populates="bookings")

    def __str__(self): # для отображения в админке
        return f"Booking #{self.id}"
