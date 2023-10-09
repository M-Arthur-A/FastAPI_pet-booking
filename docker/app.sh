#!/usr/bin/bash
poetry run alembic upgrade head

poetry run gunicorn app.main:app --workers 10 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8050
