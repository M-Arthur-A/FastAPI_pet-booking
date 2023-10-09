import json
import csv
from datetime import datetime
from io import StringIO
from typing import Literal

from fastapi import UploadFile
from sqlalchemy import MetaData, Table, insert
from sqlalchemy.exc import SQLAlchemyError

from app.database import async_session_maker, engine
from app.exceptions import CannotProcessCSV
from app.repo.base import BaseDAO
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from app.logger import logger


class ImporterDAO(BaseDAO):
    @classmethod
    async def filler_csv(cls,
                         table: Literal['hotels', 'rooms'],
                         file: UploadFile):
        if table == 'hotels':
            model: Hotels = Hotels
        elif table == 'rooms':
            model: Rooms = Rooms
        else:
            raise CannotProcessCSV

        buffer = StringIO(file.file.read().decode('utf-8'))
        data = cls._parse_data(csv.DictReader(buffer, delimiter=","))

        try:
            query = insert(model).values(data).returning(model.id)
            async with async_session_maker() as session:
                result = await session.execute(query)
                await session.commit()
                return result.mappings().first()
        except (SQLAlchemyError, Exception) as e:
            msg = 'error'
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot bulk insert data into table"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot bulk insert data into table"
            logger.error(msg, extra={"table": model.__tablename__}, exc_info=True)
            return None


    @classmethod
    def _parse_data(cls, csv_iterable):
        data = []
        for row in csv_iterable:
            for key, val in row.items():
                if val.isdigit():
                    row[key] = int(val)
                elif key == "services":
                    row[key] = json.loads(val.replace("'", '"').replace(";", ","))
                elif "date" in key:
                    row[key] = datetime.strptime(val, "%Y-%m-%d")
            data.append(row)
        return data
