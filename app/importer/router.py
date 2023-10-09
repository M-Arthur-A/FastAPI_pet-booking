from typing import Literal
from fastapi import APIRouter, Depends, UploadFile

from app.importer.repo import ImporterDAO
from app.users.models import Users
from app.users.dependencies import get_current_user




router = APIRouter(
    prefix="/import",
    tags=["Загрузка"],
)



@router.post("/csv")
async def fill_with_csv(table: Literal['hotels', 'rooms'],
                     file: UploadFile,
                     user: Users = Depends(get_current_user)):
    await ImporterDAO.filler_csv(table=table, file=file)
