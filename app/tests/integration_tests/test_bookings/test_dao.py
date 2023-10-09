from datetime import datetime

from app.bookings.repo import BookingDAO



async def test_add_and_get_booking():
    new_booking = await BookingDAO.add(
        user_id=2,
        room_id=2,
        date_from=datetime.strptime('2023-07-10', '%Y-%m-%d'),
        date_to=datetime.strptime('2023-07-24', '%Y-%m-%d'),
    )
    assert new_booking['user_id'] == 2
    assert new_booking['room_id'] == 2

    new_booking = await BookingDAO.find_by_id(new_booking.id)
    assert new_booking is not None


async def test_CRUD():
    """
    Create, Read, Update, Delete operations with bookings
    """
    new_booking = await BookingDAO.add(
        user_id=1,
        room_id=1,
        date_from=datetime.strptime('2023-07-10', '%Y-%m-%d'),
        date_to=datetime.strptime('2023-07-24', '%Y-%m-%d'),
    )
    get_bookings = await BookingDAO.find_all(user_id=1)
    assert new_booking['id'] == get_bookings[0]['id']

    del_booking = await BookingDAO.delete(user_id=1,
                                          booking_id=new_booking['id'])
    get_bookings = await BookingDAO.find_all(user_id=1)
    assert len(get_bookings) == 0
