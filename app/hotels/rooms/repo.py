from datetime import date
from sqlalchemy import select, func, insert
from sqlalchemy.exc import SQLAlchemyError

from app.repo.base import BaseDAO
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from app.bookings.models import Bookings
from app.database import async_session_maker, engine


class RoomDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def find_all(cls,
                       hotel_id:  int,
                       date_from: date,
                       date_to:   date):
        """
        with rooms_booked as
        (SELECT r.id, count(r.id) as "booked"
        FROM bookings as b
        LEFT OUTER JOIN rooms as r ON b.room_id = r.id
        WHERE r.hotel_id = 1 and b.date_from <= '2023-06-15' AND b.date_to >= '2023-05-20'
        GROUP BY r.id)
        SELECT r.id, r.hotel_id, r.name, r.description, r.services, r.price, r.quantity, r.image_id,
            r.price * (DATE '2023-06-15' - DATE '2023-05-20') as "total_cost",
            r.quantity - coalesce(temp.booked, 0) as "rooms_left"
        from rooms as r
        LEFT JOIN rooms_booked as temp ON r.id = temp.id
        WHERE r.hotel_id = 1;
        """
        rooms_booked = select(Rooms.id, func.count(Rooms.id).label('booked')).\
            select_from(Bookings).\
            join(Rooms, Bookings.room_id == Rooms.id, isouter=True).\
            where((Rooms.hotel_id == hotel_id) & (Bookings.date_from <= date_to) & (Bookings.date_to >= date_from)).\
            group_by(Rooms.id).cte('rooms_booked')
        query = select(Rooms.id, Rooms.hotel_id, Rooms.name, Rooms.description, Rooms.services,
                       Rooms.price, Rooms.quantity, Rooms.image_id,
                       (Rooms.price * (func.date(date_to) - func.date(date_from))).label('total_cost'),
                       (Rooms.quantity - func.coalesce(rooms_booked.c.booked, 0)).label('rooms_left')).\
            select_from(Rooms).\
            join(rooms_booked, Rooms.id == rooms_booked.c.id, isouter=True).\
            where(Rooms.hotel_id == hotel_id)

        # print(query.compile(engine, compile_kwargs={"literal_binds": True}))

        async with async_session_maker() as session:
            result = await session.execute(query)
            return result.mappings().all()
