from abc import ABC, abstractmethod


class BookRepository(ABC):

    @abstractmethod
    async def create_book(self, book_name: str) -> str:
        ...

    @abstractmethod
    async def delete_book(self, book_id: str) -> int:
        ...

    @abstractmethod
    async def insert_pages(self, pages: list[dict]) -> int:
        ...

    @abstractmethod
    async def delete_pages(self, book_id: str) -> int:
        ... 

    @abstractmethod
    async def get_page(self, book_id: str, page: int) -> dict | None:
        ...

    