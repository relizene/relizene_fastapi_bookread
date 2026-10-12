from fastapi import APIRouter
from app.api.v1 import books

api_router = APIRouter()
api_router.include_router(books.router)