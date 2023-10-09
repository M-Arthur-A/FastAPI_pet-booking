from datetime import datetime

from fastapi import UploadFile
from httpx import AsyncClient

from app.importer.repo import ImporterDAO
from app.hotels.repo import HotelDAO
from app.main import get_hotels



async def test_csv_filler(authenticated_ac: AsyncClient):
    get_hotels = await HotelDAO.find_all(location="Алтай",
                                         date_from=datetime.strptime('2000-01-01', '%Y-%m-%d'),
                                         date_to=datetime.strptime('2100-01-01', '%Y-%m-%d'))

    with open('app/tests/mock_hotels.csv', 'rb') as file_obj:
        response = await authenticated_ac.post('/import/csv',
                                               params={'table': 'hotels'},
                                               files={"file": ("filename", file_obj, "text/csv")})
    assert response.status_code == 200

    get_hotels_new = await HotelDAO.find_all(location="Алтай",
                                         date_from=datetime.strptime('2000-01-01', '%Y-%m-%d'),
                                         date_to=datetime.strptime('2100-01-01', '%Y-%m-%d'))
    assert len(get_hotels) + 3 == len(get_hotels_new)
