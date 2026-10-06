from fastapi import FastAPI
from pydantic import  BaseModel
import uvicorn
from contextlib import asynccontextmanager
from fastapi import Depends

from app.domain.books.service import BookService
from app.infractructure.db import mongo
from app.core.dependencies import get_book_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo.connect()
    yield
    mongo.close()

app = FastAPI(lifespan=lifespan)


class BookModels(BaseModel):
    book_name: str
    content: str
@app.post('/books-upload/')
async def upload_books(
    metadata: BookModels,
    service: BookService = Depends(get_book_service)
    ) :
    """Загрузка страницы в базу данных. Приходит данные в формате base64. Модуль pdf форматер переводит его
    в пдф и с помощью модуля pymypdf постранично сохраняет его"""

    try:
        result = await service.upload(metadata.book_name, metadata.content)
        if result['extraction_failed']:
            return {'message' : 'Не удалось извлечь страницы из pdf', 'cod' : '1006'}
        return {
            'message' : 'Книга сохранена',
            'сохраненные страницы' : f"{result['saved_pages']}",
            'cod' : '1001',
            'id книги' : result['book_id'],
        }
    except Exception as e:
        return {'message' : f' Внутренняя ошибка базы данных: {str(e)}', 'cod' : '1005',}


    
    

class BookDeleteModels(BaseModel):
    id : str
    pages : str
@app.post('/books-delete/')
async def delete_books(
    metadata: BookDeleteModels,
    service: BookService = Depends(get_book_service)
    ):
    """Функция для удаления страниц книги и самой книги"""
    try:
        excpected = int(metadata.pages)
        result = await service.delete(metadata.id)
        deleted_pages = result['deleted_pages']
        if result['book_deleted']:
            return {
                "message" : f"Книга удалена, удаленных странниц {deleted_pages}", 'cod' : '2001',
            }
        if deleted_pages == excpected:
            return {
                'message' : f'книга не удалена, но страницы все удалены! Удаленных страниц {deleted_pages}',
                'cod' : '2003',
                'delete_count' : f'{deleted_pages}'
            }
        return {
            'message': f'страницы удалились в количестве {deleted_pages}, а сама книга нет',
            'cod' : '2002',
            'deleted_count' : f'{deleted_pages}',
        }
    except Exception as e:
        return {'message' : f'Ошибка базы данных: {str(e)},', 'cod' : '2004'}
    

class BookGetPage(BaseModel):
    page: str
    book_id : str
@app.post('/get_page/')
async def get_page(
    metadata: BookGetPage,
    service: BookService = Depends(get_book_service),
    ):
    try:
        page = await service.get_page(metadata.book_id, int(metadata.page))
        if page:
            return {
            'page_number' : page.get('page'),
            'cod' : '3001',
            'content' : page.get('content'),
            }
        return {'message' : 'Страница не найдена', 'cod' : '3002'}
    except Exception as e:
        """Ошибки pyMongo"""
        return {'message': f'Ошибка базы данных: {str(e)}', 'cod': '3003'}


if __name__ == '__main__':
    uvicorn.run('app.main:app', reload=True)





