from httpx import AsyncClient

async def test_client_works(client: AsyncClient):
    response= await client.post(
        "/api/v1/books/upload/",
        json= {"book_name": "Test", "content": "fake"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["cod"] == "1001"
    assert body["book_id"]
