from datetime import date
from sqlalchemy import delete, select, and_, or_, func, insert
from sqlalchemy.exc import SQLAlchemyError

from app.repo.base import BaseDAO
from app.bookings.models import Bookings
from app.database import async_session_maker, engine
from app.hotels.rooms.models import Rooms
from app.exceptions import RoomFullyBooked
from app.logger import logger



class BookingDAO(BaseDAO):
    model = Bookings


    @classmethod
    async def find_all(cls, user_id: int):
        """
        select b.id, b.room_id, b.user_id, b.date_from, b.date_to, b.price, b.total_cost, b.total_days,
        r.image_id, r.name, r.description, r.services
        from bookings as b
        left join rooms as r
        on r.id = b.user_id
        where b.user_id = 1;
        """
        query = select(Bookings.id, Bookings.room_id, Bookings.user_id, Bookings.date_from,
                       Bookings.date_to, Bookings.price, Bookings.total_cost, Bookings.total_days,
                       Rooms.image_id, Rooms.name, Rooms.description, Rooms.services).\
            join(Rooms, Bookings.room_id == Rooms.id, isouter=True).\
            where(Bookings.user_id == user_id)

        # print(query.compile(engine, compile_kwargs={"literal_binds": True}))

        async with async_session_maker() as session:
            result = await session.execute(query)
            return result.mappings().all()


    @classmethod
    async def add(
        cls,
        user_id: int,
        room_id: int,
        date_from: date,
        date_to: date,
    ):
        """
        WITH booked_rooms AS (
            SELECT * FROM bookings
            WHERE room_id = 1 AND
                (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
                (date_from <= '2023-05-15' AND date_to > '2023-05-15')
        )
        SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms
        LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
        WHERE rooms.id = 1
        GROUP BY rooms.quantity, booked_rooms.room_id
        """
        try:
            async with async_session_maker() as session:
                booked_rooms = (
                    select(Bookings)
                    .where(
                        and_(
                            Bookings.room_id == room_id,
                            or_(
                                and_(
                                    Bookings.date_from >= date_from,
                                    Bookings.date_from <= date_to,
                                ),
                                and_(
                                    Bookings.date_from <= date_from,
                                    Bookings.date_to > date_from,
                                ),
                            ),
                        )
                    )
                    .cte("booked_rooms")
                )
                # cte - WITH, временная таблица. запросы к колонкам из нее потом делаются через ...c...

                """
                SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms
                LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
                WHERE rooms.id = 1
                GROUP BY rooms.quantity, booked_rooms.room_id
                """

                get_rooms_left = (
                    select(
                        (Rooms.quantity - func.count(booked_rooms.c.room_id)).label(
                            "rooms_left"
                        )
                    )
                    .select_from(Rooms)
                    .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
                    .where(Rooms.id == room_id)
                    .group_by(Rooms.quantity, booked_rooms.c.room_id)
                )
                # показать сгенерированный алхимией запрос
                # print(get_rooms_left.compile(engine, compile_kwargs={"literal_binds": True}))
                rooms_left_raw = await session.execute(get_rooms_left)
                rooms_left: int | None = rooms_left_raw.scalar()

                if rooms_left and rooms_left > 0:
                    get_price = select(Rooms.price).filter_by(id=room_id)
                    price = await session.execute(get_price)
                    price: int = price.scalar()
                    add_booking = (
                        insert(Bookings)
                        .values(
                            room_id=room_id,
                            user_id=user_id,
                            date_from=date_from,
                            date_to=date_to,
                            price=price,
                        )
                        .returning(
                            Bookings.id,
                            Bookings.user_id,
                            Bookings.room_id,
                            Bookings.date_from,
                            Bookings.date_to,
                        )
                    )

                    new_booking = await session.execute(add_booking)
                    await session.commit()
                    return new_booking.mappings().one()
                else:
                    raise RoomFullyBooked
        except RoomFullyBooked:
            raise RoomFullyBooked
        except (SQLAlchemyError, Exception) as e:
            msg = ""
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            elif isinstance(e, Exception):
                msg = "Unknown Exc"
            extra = {
                "user_id": user_id,
                "room_id": room_id,
                "date_from": date_from,
                "date_to": date_to,
            }
            msg += ": Cannot add booking"
            logger.error(
                msg,
                extra=extra,
                exc_info=True,
            )


    @classmethod
    async def delete(cls, user_id: int, booking_id: int):
        query = delete(Bookings).where((Bookings.user_id == user_id) & (Bookings.id == booking_id))
        async with async_session_maker() as session:
            await session.execute(query)
            await session.commit()
