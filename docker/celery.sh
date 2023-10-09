#!/usr/bin/bash

if [[ "${1}" == "celery" ]]; then
poetry run celery --app=app.tasks.celery:celery worker -l INFO
elif [[ "${1}" == "flower" ]]; then
poetry run celery --app=app.tasks.celery:celery flower
fi
