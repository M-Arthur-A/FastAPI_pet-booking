FROM python:3.11

RUN mkdir /booking

WORKDIR /booking

COPY poetry.lock .
COPY pyproject.toml .

RUN pip install poetry
RUN poetry install

COPY . .

RUN chmod a+x /booking/docker/*.sh

CMD ["poetry", "run", "gunicorn", "app.main:app", "--workers", "10", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8050"]
