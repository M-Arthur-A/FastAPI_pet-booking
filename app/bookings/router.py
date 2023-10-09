from datetime import date
from fastapi import APIRouter, Depends
from pydantic import parse_obj_as

from app.bookings.repo import BookingDAO
from app.users.models import Users
from app.users.dependencies import get_current_user
from app.bookings.schemas import SBooking
from app.exceptions import CannotBookHotelForLongPeriod, DateFromCannotBeAfterDateTo, RoomCannotBeBooked, NoBookings

router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"], # объединение роутеров под таким тегом в документации (swagger)
)

@router.get("")
async def get_bookings(user: Users = Depends(get_current_user)) -> list[SBooking]:
    # return await BookingDAO.find_one_or_none(room_id=1)
    # return await BookingDAO.find_by_id(1)
    bookings = await BookingDAO.find_all(user_id=user.id)
    if not bookings:
        raise NoBookings
    return bookings

@router.post("")
async def add_booking(
        room_id: int, date_from: date, date_to: date,
        user: Users = Depends(get_current_user),
):
    if date_to < date_from:
        raise DateFromCannotBeAfterDateTo
    if (date_to - date_from).days > 30:
        raise CannotBookHotelForLongPeriod

    booking = await BookingDAO.add(user.id, room_id, date_from, date_to)
    if not booking:
        raise RoomCannotBeBooked
    return booking

@router.delete("/{booking_id}")
async def del_booking(booking_id: int,
                      user: Users = Depends(get_current_user)):
    await BookingDAO.delete(user.id, booking_id)
