from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import get_book_repository
from app.domain.books.repository import BookRepository
from app.main import create_app


class FakeBookRepository(BookRepository):
    """Реализация для тестов"""
    def __init__(self) -> None:
        self._books: dict[str, str] = {}
        self._pages: list[dict] = []
        self._next_id = 0

    def _new_id(self) -> str:
        self._next_id += 1
        return f"{self._next_id:024x}"

    async def create_book(self, book_name: str)-> str:
        book_id = self._new_id()
        self._books[book_id] = book_name
        return book_id

    async def delete_book(self, book_id: str) -> int:
        if book_id in self._books:
            del self._books[book_id]
            return 1
        return 0

    async def insert_pages(self, pages: list[dict]) -> int:
        if not pages:
            return 0
        self._pages.extend(pages)
        return len(pages)

    async def delete_pages(self, book_id: str) -> int:
        before = len(self._pages)
        self._pages = [p for p in self._pages if str(p["book_id"]) != book_id]
        return before - len(self._pages)

    async def get_page(self, book_id: str, page: int) -> dict | None:
        for p in self._pages:
            if str(p["book_id"]) == book_id and p["page"] == page:
                return p
        return None


@pytest.fixture
def fake_repo() -> FakeBookRepository:
    """Свежий фейковый репозиторий для каждого теста"""
    return FakeBookRepository()


@pytest.fixture
def app(fake_repo: FakeBookRepository, monkeypatch: pytest.MonkeyPatch):
    """Fastapi app с подмененным репозиторием и PDF парсером"""
    def fake_pdf_parser(content: str, book_name: str, book_id) -> list[dict]:
        return [
            {"book_id": book_id, "page": 1, "content": f"<p>{book_name} p1</p>"},
            {"book_id": book_id, "page": 2, "content": f"<p>{book_name} p2</p>"},
        ]
    monkeypatch.setattr(
        "app.domain.books.service.pdf_formater",
        fake_pdf_parser,
    )
    app = create_app()
    app.dependency_overrides[get_book_repository] = lambda: fake_repo
    return app

@pytest_asyncio.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    """Асинхронный HTTP клиент для тестирования API"""
    async with AsyncClient(
        transport= ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c