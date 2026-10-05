from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.books.repository import BookRepository


class MongoBookRepository(BookRepository):

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._books = db.book
        self._pages = db.pages

    async def create_book(self, book_name: str)-> str:
        result = await self._books.insert_one({'book_name' : book_name})
        return str(result.inserted_id)

    async def delete_book(self, book_id: str)-> int:
        result = await self._books.delete_one({'id': ObjectId(book_id)})
        return result.deleted_count

    async def insert_pages(self, pages: list[dict])-> int:
        if not pages:
            return 0
        result = await self._pages.insert_many(pages) 
        return len(result.inserted_ids)

    async def delete_pages(self, book_id: str)-> int:
        result = await self._pages.delete_many({'book_id' : ObjectId(book_id)})
        return result.deleted_count
    
    async def get_page(self, book_id:  str, page: int)-> dict | None:
        result = await self._pages.find_one({
            "book_id": ObjectId(book_id),
            "page" : page,
        })
        return result