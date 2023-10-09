import pytest
from httpx import AsyncClient



@pytest.mark.parametrize('room_id,date_from,date_to,booked_rooms,status_code', *[
    [(4, "2030-05-01", f"2030-05-15", i, 200) for i in range(3, 11)] +
    [(4, "2030-05-01", "2030-05-15",  10, 409)] * 2 +
    [(1, "2030-06-01", "2030-05-15",  10, 400)] +
    [(1, "2030-05-01", "2030-08-15",  10, 400)] +
    [(1, "2030-05-01", "2030-05-15",  11, 200)]
])
async def test_add_and_get_booking(room_id, date_from, date_to, booked_rooms, status_code,
                                   authenticated_ac: AsyncClient):
    response = await authenticated_ac.post('/bookings', params={
        'room_id': room_id,
        'date_from': date_from,
        'date_to': date_to,
    })
    assert response.status_code == status_code

    response = await authenticated_ac.get('/bookings')
    assert len(response.json()) == booked_rooms


async def test_booking_deletions(authenticated_ac: AsyncClient):
    bookings_all = await authenticated_ac.get('/bookings')
    assert bookings_all.status_code == 200

    for booking in bookings_all.json():
        response = await authenticated_ac.delete(f'/bookings/{booking["id"]}')
        assert response.status_code == 200

    response = await authenticated_ac.get('/bookings')
    assert response.json() == {'detail': 'У данного пользователя отсутствуют бронирования'}
