![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-red)
![MongoDB](https://img.shields.io/badge/MongoDB-4.4-green)
![Docker](https://img.shields.io/badge/Docker-✓-blue)
![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

# Books Microservice

Асинхронный микросервис для управления PDF-книгами: загрузка, постраничное хранение, извлечение контента. Построен на FastAPI + MongoDB со слоистой архитектурой и полным покрытием тестами.

## 🚀 Возможности

- Загрузка PDF-книг с конвертацией в HTML (постранично)
- Постраничное хранение и извлечение контента
- Валидация входящих данных через Pydantic
- Единый exception handler для доменных ошибок
- Структурированное логирование
- Healthcheck для мониторинга
- Docker с healthchecks
- Покрытие тестами (93%, unit + e2e)

## 🛠 Технологии

- **FastAPI** — асинхронный веб-фреймворк
- **Pydantic v2** — валидация и схемы
- **Motor** — асинхронный драйвер MongoDB
- **PyMuPDF** — обработка PDF
- **MongoDB** — хранилище
- **pytest** + **pytest-asyncio** — тесты
- **Docker** + **docker-compose** — контейнеризация

## 📦 Установка и запуск

### Локальная разработка

```bash
# Клонирование
git clone https://github.com/yourusername/relizene_fastapi_bookread.git
cd relizene_fastapi_bookread

# Виртуальное окружение
python -m venv venv
source venv/bin/activate      # Linux/macOS
# или
venv\Scripts\activate         # Windows

# Зависимости
pip install -r requirements.txt

# Настройки
cp .env.example .env

# MongoDB (нужен Docker)
docker compose up -d mongodb

# Запуск приложения
uvicorn app.main:app --reload
```

Приложение доступно на `http://localhost:8000`.

### Docker

```bash
# Запуск всех сервисов (MongoDB + приложение)
docker compose up --build -d

# Статус (должно быть healthy у обоих)
docker compose ps

# Логи
docker compose logs -f books-service

# Остановка
docker compose down
```

## 🔌 API

Базовый префикс: `/api/v1`.

### Загрузка книги

```http
POST /api/v1/books/upload/
Content-Type: application/json

{
  "book_name": "Война и мир",
  "content": "<base64 PDF>"
}
```

Ответ (`200 OK`):
```json
{
  "message": "Книга сохранена",
  "cod": "1001",
  "book_id": "507f1f77bcf86cd799439011",
  "saved_pages": "10"
}
```

### Удаление книги

```http
POST /api/v1/books/delete/
Content-Type: application/json

{
  "id": "507f1f77bcf86cd799439011",
  "pages": 10
}
```

Ответ (`200 OK`):
```json
{
  "message": "Книга удалена, удаленных страниц 10",
  "cod": "2001"
}
```

### Получение страницы

```http
POST /api/v1/books/page/
Content-Type: application/json

{
  "book_id": "507f1f77bcf86cd799439011",
  "page": 1
}
```

Ответ (`200 OK`):
```json
{
  "cod": "3001",
  "page_number": 1,
  "content": "<p>...</p>"
}
```

### Healthcheck

```http
GET /api/v1/health
```

Ответ (`200 OK`):
```json
{"status": "ok"}
```

## 📊 Коды ответов

| Код | Значение |
|-----|----------|
| `1001` | Книга сохранена |
| `1005` | Внутренняя ошибка БД (upload) |
| `1006` | Не удалось извлечь страницы из PDF |
| `2001` | Книга и страницы удалены |
| `2002` | Страницы удалены, книга нет (несовпадение количества) |
| `2003` | Страницы удалены, книга не найдена |
| `2004` | Ошибка БД (delete) |
| `3001` | Страница найдена |
| `3002` | Страница не найдена |
| `3003` | Ошибка БД (page) |

**Ошибки валидации входящих данных** возвращают `422` с полем `detail` от Pydantic.

## 📚 Документация API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## ⚙️ Переменные окружения

Скопируй `.env.example` в `.env`:

```
APP_NAME=Books Microservice
DEBUG=false
MONGO_URL=mongodb://localhost:27017
MONGO_DB=book_library
```

## 🧪 Тесты

```bash
# Все тесты (с coverage)
pytest

# Подробно
pytest -v

# Только unit
pytest tests/unit/ -v

# Только e2e
pytest tests/e2e/ -v

# HTML-отчёт coverage
pytest --cov=app --cov-report=html
# открыть htmlcov/index.html

# Только упавшие в прошлый раз
pytest --lf

# Замеры скорости
pytest --durations=10
```

Покрытие по бизнес-логике — **93%**. Тесты работают **без реальной MongoDB** (используется `FakeBookRepository`) и **без парсинга настоящих PDF** (`monkeypatch`).

## 🏗 Структура проекта

```
app/
├── main.py                     # create_app, lifespan
│
├── core/                       # инфраструктура приложения
│   ├── config.py               # настройки (pydantic-settings)
│   ├── dependencies.py         # DI-фабрики
│   ├── exceptions.py           # handler доменных ошибок
│   └── logging.py              # настройка логирования
│
├── api/
│   └── v1/
│       ├── __init__.py         # api_router
│       ├── books.py            # роуты книг
│       ├── health.py           # healthcheck
│       └── schemas.py          # Pydantic-схемы (вход/выход)
│
├── domain/
│   └── books/
│       ├── repository.py       # интерфейс BookRepository (ABC)
│       ├── service.py          # BookService — бизнес-логика
│       └── exceptions.py       # доменные исключения
│
└── infrastructure/
    ├── db.py                   # Mongo singleton
    ├── repositories/
    │   └── book_repo.py        # MongoBookRepository
    └── pdf/
        └── parser.py           # pdf_formater (PyMuPDF)

tests/
├── conftest.py                 # FakeBookRepository + фикстуры
├── test_smoke.py               # smoke
├── unit/                       # тесты сервиса
└── e2e/                        # тесты API через AsyncClient
```

## 🧩 Архитектура

Слоистая:

```
HTTP-запрос
    ↓
api/v1/books.py       ← принимает, валидирует, вызывает сервис
    ↓
domain/books/service.py    ← бизнес-логика
    ↓
domain/books/repository.py ← интерфейс
    ↓
infrastructure/repositories/book_repo.py  ← реализация (Mongo)
    ↓
MongoDB
```

**Правило зависимостей:**

```
api  →  domain  →  infrastructure
         ↑
        core
```

- `api` знает про `domain` и `core`, **не знает** про `infrastructure` напрямую.
- `domain` знает про `infrastructure` (через интерфейсы) и `core`, **не знает** про `api`.
- `infrastructure` знает только `core`.
- `core` — общий для всех.

**Что это даёт:**
- **Заменяемость.** Переход на Postgres — правится только `book_repo.py`.
- **Тестируемость.** `BookService` тестируется с `FakeBookRepository`, без Mongo.
- **Изоляция ошибок.** Доменные ошибки → `BookError`, обрабатываются единым handler.

## 🐳 Docker healthchecks

Оба сервиса имеют healthcheck:

- `mongodb` — `mongo --eval "db.adminCommand('ping')"`.
- `books-service` — `GET /api/v1/health`.

`books-service` стартует **только после** того, как MongoDB станет `healthy`.

## 📄 Лицензия

MIT