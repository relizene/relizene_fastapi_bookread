import pytest

from app.domain.books.service import BookService
from app.domain.books.exceptions import PageNotFound, PdfExctractionFailed
from tests.conftest import FakeBookRepository


#---------------Тест ручки upload-----------------

async def test_upload_success(fake_repo: FakeBookRepository, monkeypatch):
    """Успешная загрузка: книга создана страницы вставлены"""
    def fake_pdf_formater(content: str, book_name: str, book_id) -> list[dict]:
        return [
            {"book_id": book_id, "page": 1, "content": "<p>p1</p>"},
            {"book_id": book_id, "page": 2, "content": "<p>p2</p>"},
        ]
    monkeypatch.setattr(
        "app.domain.books.service.pdf_formater",
        fake_pdf_formater,
    )
    service = BookService(fake_repo)
    result = await service.upload("Test Book", "fake-base64")
    assert result["saved_pages"] == 2
    assert "book_id" in result
    assert result["book_id"] in fake_repo._books


async def test_upload_pdf_exctraction_failed(fake_repo: FakeBookRepository, monkeypatch):
        """Парсинг вернул пустой список: книга откатывается"""
        def fake_pdf_formater_empty(content: str, book_name: str, book_id) ->list[dict]:
            return []
        monkeypatch.setattr(
            "app.domain.books.service.pdf_formater",
            fake_pdf_formater_empty,
        )
        service = BookService(fake_repo)
        with pytest.raises(PdfExctractionFailed):
             await service.upload("Test Book", "fake-base-64")
        assert len(fake_repo._books) == 0  
        assert len(fake_repo._pages) == 0

async def test_upload_pdf_fotmater_raises(fake_repo: FakeBookRepository, monkeypatch):
        """Парсинг упал: книга откатывается. Исключение пробрасывается"""

        def fake_pdf_formarer_raises(content: str, book_name: str, book_id) -> list[dict]:
            raise RuntimeError("PDF parser broke")

        monkeypatch.setattr(
            "app.domain.books.service.pdf_formater",
            fake_pdf_formarer_raises,
        )
        service = BookService(fake_repo)
        with pytest.raises(RuntimeError, match="PDF parser broke"):
             await service.upload("Test Book", "fake-base64")

        assert len(fake_repo._books) == 0


#-------------------------Тест ручки delete-----------------------


async def test_delete_success(fake_repo: FakeBookRepository):
    """Количество совпало: страницы и книги удалены."""
    book_id = await fake_repo.create_book("Test")
    await fake_repo.insert_pages([
        {"book_id": book_id, "page": 1, "content": "p1"},
        {"book_id": book_id, "page": 2, "content": "p2"},
    ])
    service = BookService(fake_repo)
    result = await service.delete(book_id, excepted_pages=2)
    assert result["deleted_pages"] == 2
    assert result["book_deleted"] is True
    assert book_id not in fake_repo._books

async def test_delete_count_dismatch(fake_repo: FakeBookRepository):
    """Количество не совпало: страницы удалены, книга осталась"""
    book_id = await fake_repo.create_book("Test")
    await fake_repo.insert_pages([
        {"book_id": book_id, "page": 1, "content": "p1"},
        {"book_id": book_id, "page": 2, "content": "p2"},
    ])
    service = BookService(fake_repo)
    result = await service.delete(book_id, excepted_pages=5)
    assert result["deleted_pages"] == 2
    assert result["book_deleted"] is False
    assert book_id in fake_repo._books


#-------------------Тест ручки get_page--------------


async def test_get_page(fake_repo: FakeBookRepository):
    """Страница найдена"""
    book_id = await fake_repo.create_book("Test")
    await fake_repo.insert_pages([
         {"book_id": book_id, "page": 1, "content": "<p>content</p>"},
    ])
    service = BookService(fake_repo)
    result = await service.get_page(book_id, 1)
    assert result is not None
    assert result["content"] == "<p>content</p>"


async def test_get_page_not_found(fake_repo: FakeBookRepository):
    """Страница не найдена"""
    book_id = await fake_repo.create_book("Test")
    service = BookService(fake_repo)
    with pytest.raises(PageNotFound):
         await service.get_page(book_id, 999)

