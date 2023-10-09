from fastapi import APIRouter, UploadFile
import shutil

from app.tasks.tasks import process_pic

router = APIRouter(
    prefix="/import",
    tags=["Загрузка"],
)

@router.post("/img")
async def add_hotel_img(name: int, file: UploadFile):
    img_path = f'app/static/images/{name}.webp'
    with open(img_path, 'wb+') as file_obj:
        shutil.copyfileobj(file.file, file_obj)

    # передача в Celery
    process_pic.delay(img_path)
