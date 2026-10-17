import asyncio
import logging
from bson import ObjectId

from app.domain.books.exceptions import BookError, PageNotFound, PdfExctractionFailed
from app.domain.books.repository import BookRepository
from app.infractructure.pdf.parser import pdf_formater


logger = logging.getLogger(__name__)


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
                logger.info("Book upload: id=%s, pages=%d", book_id, saved)
                return {
                    'book_id' : book_id,
                    'saved_pages' : saved,
                }
            await self.repo.delete_book(book_id)
            logger.info("PDF Exctraction failed for book_name=%s, rolled back", book_name)
            raise PdfExctractionFailed()
        except BookError:
            raise
        except Exception:
            if book_id is not None:
                await self.repo.delete_book(book_id)
            raise

    async def delete(self, book_id: str, excepted_pages: int) -> dict:
        deleted_pages = await self.repo.delete_pages(book_id)
        if deleted_pages == excepted_pages:
            deleted_book = await self.repo.delete_book(book_id)
            logger.info(
                "Book deleted: id=%s, pages=%d, book_deleted=%s",
                book_id, deleted_pages, deleted_book==1,
            )
            return {
                'deleted_pages' : deleted_pages,
                'book_deleted' : deleted_book == 1,
            }
        return {
            'deleted_pages' : deleted_pages,
            'book_deleted' : False
        }

    async def get_page(self, book_id: str, page: int) -> dict:
        page_doc= await self.repo.get_page(book_id, page)
        if page_doc is None:
            raise PageNotFound()
        return page_doc
        
    
