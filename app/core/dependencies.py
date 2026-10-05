from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.books.repository import BookRepository
from app.infractructure.db import mongo
from app.infractructure.repositories.book_repo import MongoBookRepository


def get_database() -> AsyncIOMotorDatabase:
    return mongo.db


def get_book_repository(
        db: AsyncIOMotorDatabase = Depends(get_database),
) -> BookRepository:
    return MongoBookRepository(db)

