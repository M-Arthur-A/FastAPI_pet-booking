from datetime import date
from fastapi import APIRouter

from app.hotels.rooms.repo import RoomDAO
from app.hotels.rooms.schemas import SRooms
from app.exceptions import RoomCannotBeBooked


router = APIRouter(
    prefix="/hotels",
    tags=["Отели"], # объединение роутеров под таким тегом в документации (swagger)
)

@router.get("/{hotel_id}/rooms")
async def get_available_rooms(hotel_id: int,
                              date_from: date,
                              date_to: date) -> list[SRooms]:
    rooms_available = await RoomDAO.find_all(hotel_id, date_from, date_to)
    if not rooms_available:
        raise RoomCannotBeBooked
    return rooms_available
