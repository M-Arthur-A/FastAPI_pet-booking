from datetime import date
from sqlalchemy import select, func, insert
from sqlalchemy.exc import SQLAlchemyError

from app.repo.base import BaseDAO
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from app.bookings.models import Bookings
from app.database import async_session_maker, engine


class HotelDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def find_all(cls,
                       location:  str,
                       date_from: date,
                       date_to:   date):
        """
        select h.id, h.name, h.location, h.services, h.rooms_quantity, h.image_id,
            (h.rooms_quantity - coalesce(temp.count, 0)) as rooms_left
        from public.hotels as h
        left join
            (select r.hotel_id, count(r.hotel_id) from public.bookings as b
            left join public.rooms as r on b.room_id = r.id)
            where (b.date_from <= '2023-06-15' and b.date_to >= '2023-05-20')
            group by r.hotel_id) as temp
        on h.id = temp.hotel_id
        where position(LOWER('алтай') in LOWER(h.location))>0;
        """

        rooms_booked = select(Rooms.hotel_id, func.count(Rooms.hotel_id).label('booked')).\
            select_from(Bookings).\
            join(Rooms, Bookings.room_id == Rooms.id, isouter=True).\
            where((Bookings.date_from <= date_to) & (Bookings.date_to >= date_from)).\
            group_by(Rooms.hotel_id).cte('rooms_booked')
        query = select(Hotels.id, Hotels.name, Hotels.location, Hotels.services,
                       Hotels.rooms_quantity, Hotels.image_id,
                       (Hotels.rooms_quantity - func.coalesce(rooms_booked.c.booked, 0)).label('rooms_left')).\
            select_from(Hotels).\
            join(rooms_booked, Hotels.id == rooms_booked.c.hotel_id, isouter=True).\
            where(func.position(func.lower(location).op('IN')(func.lower(Hotels.location))) > 0)

        # print(query.compile(engine, compile_kwargs={"literal_binds": True}))

        async with async_session_maker() as session:
            result = await session.execute(query)
            return result.mappings().all()
