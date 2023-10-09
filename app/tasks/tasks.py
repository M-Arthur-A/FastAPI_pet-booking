from PIL import Image
from pathlib import Path

from app.tasks.celery import celery

@celery.task
def process_pic(
        path:str,
):
    img_path = Path(path)
    img = Image.open(img_path)
    img_resized_big = img.resize((1000,500))
    img_resized_small = img.resize((200,100))
    img_resized_big.save(f"app/static/images/resized_1000_500_{img_path.name}")
    img_resized_small.save(f"app/static/images/resized_200_100_{img_path.name}")
