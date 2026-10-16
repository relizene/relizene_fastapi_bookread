from fastapi import APIRouter
from app.api.v1 import books, health

api_router = APIRouter()
api_router.include_router(books.router)
api_router.include_router(health.router)