![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)
![MongoDB](https://img.shields.io/badge/MongoDB-4.4-green)
![Docker](https://img.shields.io/badge/Docker-✓-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

# Books Microservice

Асинхронный микросервис для управления книгами в формате PDF с использованием FastAPI и MongoDB.

## 🚀 Возможности

- Загрузка PDF книг с конвертацией в HTML
- Постраничное хранение и извлечение контента
- Асинхронные операции с базой данных
- Docker контейнеризация
- Полная документация API (Swagger)

## 🛠 Технологии

- **FastAPI** - асинхронный web-фреймворк
- **Motor** - асинхронный драйвер MongoDB
- **PyMuPDF** - обработка PDF файлов
- **Docker** - контейнеризация
- **MongoDB** - база данных

## 📦 Установка и запуск

### Локальная разработка

```bash
# Клонирование репозитория
git clone https://github.com/yourusername/books-microservice.git
cd books-microservice

# Установка зависимостей
pip install -r requirements.txt

# Запуск MongoDB (требуется установленный Docker)
docker-compose up -d mongodb

# Запуск приложения
uvicorn main:app --reload


Docker запуск
# Запуск всех сервисов
docker-compose up -d

# Остановка
docker-compose down


🔌 API Endpoints
Загрузка книги
POST /books-upload/

Загружает PDF книгу и сохраняет постранично в базу

Удаление книги
POST /books-delete/

Удаляет книгу и все связанные страницы

Получение страницы
POST /get_page/

Возвращает конкретную страницу книги в формате HTML

📚 Документация API
После запуска приложения документация доступна по адресам:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

🏗 Архитектура
text
FastAPI (ASGI) → Motor → MongoDB
       ↓
   PyMuPDF (PDF processing)


Получение страницы
bash
curl -X POST "http://localhost:8000/get_page/" \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": "507f1f77bcf86cd799439011",
    "page": "1"
  }'

### Локальная разработка
```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск в режиме разработки
uvicorn main:app --reload
