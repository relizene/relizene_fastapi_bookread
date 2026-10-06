import asyncio
from bson import ObjectId

from app.domain.books.repository import BookRepository
from app.infractructure.pdf.parser import pdf_formater


class BookService:
    def __init__(self, repo: BookRepository)-> None:
        self.repo = repo

    async def upload(self, book_name: str, content: str) -> dict:
        book_id: str | None = None
        try:
            book_id = await self.repo.create_book(book_name)
            books_content = await asyncio.get_event_loop().run_in_executor(
                None,
                pdf_formater,
                content,
                book_name,
                ObjectId(book_id),
            )
            if books_content:
                saved = await self.repo.insert_pages(books_content)
                return {
                    'book_id' : book_id,
                    'saved_pages' : saved,
                    'extraction_failed' : False, 
                }
            await self.repo.delete_book(book_id)
            return {'extraction_failed' : True}
        except Exception:
            if book_id is not None:
                await self.repo.delete_book(book_id)
            raise

    async def delete(self, book_id: str, excepted_pages: int) -> dict:
        deleted_pages = await self.repo.delete_pages(book_id)
        if deleted_pages == excepted_pages:
            deleted_book = await self.repo.delete_book(book_id)
            return {
                'deleted_pages' : deleted_pages,
                'book_deleted' : deleted_book == 1,
            }
        return {
            'deleted_pages' : deleted_pages,
            'book_deleted' : False
        }

    async def get_page(self, book_id: str, page: int) -> dict | None:
        return await self.repo.get_page(book_id, page)
    
