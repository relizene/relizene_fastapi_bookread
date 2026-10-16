from httpx import AsyncClient


#----------------Тест ручки upload-------------------

async def test_upload_success(client: AsyncClient, monkeypatch):
    """Успешная загрузка книги через API"""
    response = await client.post(
        "/api/v1/books/upload/",
        json={"book_name": "Война и мир", "content": "fake-base64"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["cod"] == "1001"
    assert body["message"] == "Книга сохранена"
    assert body["book_id"] is not None


async def test_upload_extraction_failed(client: AsyncClient, monkeypatch):
    """Парсинг вернул пустой список"""

    def empty_formater(content, book_name, book_id):
        return []

    monkeypatch.setattr(
        "app.domain.books.service.pdf_formater",
        empty_formater,
    )
    response = await client.post(
        "/api/v1/books/upload/",
        json = {"book_name": "Война и мир", "content": "fake-base64"},

    )
    assert response.status_code == 200
    body = response.json()
    assert body["cod"] == "1006"
    assert body["book_id"] is None

async def test_upload_db_error(client: AsyncClient, monkeypatch):
    """Парсер бросает исключение -> 1005."""
    def raising_formater(content, book_name, book_id):
        return RuntimeError("parser broke")
    monkeypatch.setattr(
        "app.domain.books.service.pdf_formater",
        raising_formater,
    )
    response = await client.post(
        "/api/v1/books/upload/",
        json={"book_name": "Война и мир", "content": "fake-base64"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["cod"] == "1005"


#---------------Тест API delete------------

async def test_delete_success(client: AsyncClient):
    """Успешное удаление книги и страниц."""
    upload = await client.post(
        "/api/v1/books/upload/",
        json = {"book_name" : 'Test', "content" : "fake",}
    ) 
    book_id = upload.json()["book_id"]

    response = await client.post(
        "/api/v1/books/delete/",
        json={"id": book_id, "pages": "2"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["cod"] == "2001"
    assert body.get("delete_count") is None

async def test_delete_count_mismatch(client: AsyncClient):
    """Количество не совпало. Код 2002"""
    upload = await client.post(
        "/api/v1/books/upload/",
        json={"book_name" : 'Test', "content" : "fake",}
    )
    book_id = upload.json()["book_id"]
    response = await client.post(
        "/api/v1/books/delete/",
        json={"id": book_id, "pages" : "999",}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["cod"] == "2002"
    assert body["delete_count"] == "2"


#---------------------Тест API get_page----------------------


async def test_get_page(client: AsyncClient):
    """Успешное получение странцы"""
    upload = await client.post(
        "/api/v1/books/upload/",
        json={"book_name": "Test", "content": "fake"},
    )
    book_id = upload.json()["book_id"]

    response = await client.post(
        "/api/v1/books/get_page/",
        json={"book_id": book_id, "page": "1"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["cod"] == "3001"
    assert body["content"] == "<p>Test p1</p>"
    assert body["page_number"] == 1

async def test_get_page_not_found(client: AsyncClient):
    """Страница не найдена"""
    upload = await client.post(
        "/api/v1/books/upload/",
        json={"book_name": "Test", "content": "fake"},
    )
    book_id = upload.json()["book_id"]

    response = await client.post(
        "/api/v1/books/get_page/",
        json={"book_id": book_id, "page": "9999"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["cod"] == "3002"
    assert body["message"] == "Страница не найдена"

async def test_get_page_invalid_id(client: AsyncClient):
    """Невалидный id → cod 3003."""
    response = await client.post(
        "/api/v1/books/get_page/",
        json={"book_id": "not-a-valid-id", "page": "1"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["cod"] == "3002"


