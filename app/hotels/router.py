from datetime import date
from fastapi import APIRouter
from fastapi_cache.decorator import cache

from app.hotels.repo import HotelDAO
from app.hotels.schemas import SHotels
from app.exceptions import NoHotelAvailableForPeriod


router = APIRouter(
    prefix="/hotels",
    tags=["Отели"], # объединение роутеров под таким тегом в документации (swagger)
)

@router.get("/{location}")
@cache(expire=20)
async def get_hotels(location: str,
                     date_from: date,
                     date_to: date) -> list[SHotels]:
    hotels = await HotelDAO.find_all(location, date_from, date_to)
    if not hotels:
        raise NoHotelAvailableForPeriod
    # если pydantic выдает ошибку при конвертации данных в json - нужно в ручную конвертировать pydantic'ом
    # hotels = parse_obj_as(List[SHotels], hotels)
    return hotels
