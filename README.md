# Бронирование отелей
Это репозиторий тренировочного пет-проекта на Python для изучения backend-стека: `FastAPI`, `SQLadmin`, `Pydantic`, `SQLAlchemy`, `Alembic`, `PostgreSQL`, `Celery`, `Redis`, `Docker`, `Prometheus`-`Grafana`, `Pytest`. Для настройки виртуального окружения используется `Poetry`.

Реализован базовый функционал по бронированию отелей, а именно его backend.
Доступна документация swagger http://127.0.0.1:8000/docs .


## Настройка
Настройка осуществляется через редактирование двух конфигов переменных окружения в корне проекта:
- `.env`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(dev)
- `.env-non-dev` (prod)

Ниже приведены переменные окружения *(в скобках {} - указаны пользовательские данные)*
```
MODE=DEV
LOG_LEVEL=INFO

APP_HOST=127.0.0.1
APP_PORT=8000

REDIS_HOST=redis

DB_HOST=db
DB_PORT=5432
DB_USER={postgres_prod_admin}
DB_PASS={postgres_prod_admin_password}
DB_NAME=booking_app

POSTGRES_DB=booking_app
POSTGRES_USER={postgres_prod_admin}
POSTGRES_PASSWORD={postgres_prod_admin}

VOLUME_POSTGRESDATA={your-local-path-to}/postgresqldata
VOLUME_GRAFANADATA={your-local-path-to}/grafanadata
VOLUME_PROMETHEUSDATA={your-local-path-to}/prometheusdata

SECRET_KEY={secret-key}
ALGORYTM=HS256

CELERY_BROKER=redis://localhost
```

## Запуск приложения
### Для запуска в dev
Запустятся: `uvicorn`, `postgresql`, `redis`, `celery`-`flower`
```
# первичная подготовка
pip install poetry
poetry install

# запуск
poetry run python ./app.py
```

### Для запуск в prod через Docker compose
Запустятся аналогичные `Docker` контейнеры, только вместо `Uvicorn` будет `Gunicorn`
```
# первичная подготовка
sudo docker compose --env-file .env-non-dev build

# запуск
sudo docker compose --env-file .env-non-dev up
```
