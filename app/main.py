from bson import ObjectId
from fastapi import FastAPI
from pydantic import  BaseModel
import uvicorn
import asyncio
from contextlib import asynccontextmanager
from fastapi import Depends

from app.infractructure.pdf.parser import pdf_formater
from app.infractructure.db import mongo
from app.core.dependencies import get_book_repository
from app.domain.books.repository import BookRepository


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
    repo: BookRepository = Depends(get_book_repository)
    ) :
    """Загрузка страницы в базу данных. Приходит данные в формате base64. Модуль pdf форматер переводит его
    в пдф и с помощью модуля pymypdf постранично сохраняет его"""
    
    id_back: str | None = None
    try:     
        book_id = await repo.create_book(metadata.book_name)
        books_content = await asyncio.get_event_loop().run_in_executor(
            None,
            pdf_formater,
            metadata.content,
            metadata.book_name,
            ObjectId(book_id)
        )
        if books_content:
            saved = await repo.insert_pages(books_content)
            return {
                'message' : 'Книга сохранена', 
                'сохраненные страницы' : f'{saved} ',
                'id_книги' : book_id,
                'cod' : '1001'
                    }
        else:
            await repo.delete_book(book_id)
            return {'message': 'Не удалось извлечь страницы из PDF', 'cod': '1006'}
    
    except Exception as r:
        """Любая ошибка"""
        if book_id is not None:
            await repo.delete_book(book_id)
        return {'message': f' Внутреняя Ошибка базы данных: {str(r)}', 'cod': '1005'}
    
    

class BookDeleteModels(BaseModel):
    id : str
    pages : str
@app.post('/books-delete/')
async def delete_books(
    metadata: BookDeleteModels,
    repo: BookRepository = Depends(get_book_repository)
    ):
    """Функция для удаления страниц книги и самой книги"""
    try:
        delete_pages = await repo.delete_pages(metadata.id)
        if delete_pages == int(metadata.pages):
            delete_book = await repo.delete_book(metadata.id)
            if delete_book == 1:
                return {'message' : f'Книга удалена, удаленных страниц {delete_pages}', 'cod' : '2001'}
            return {
                'message' : f'Книга не удалена, но страницы удалены, удаленных страниц {delete_pages}', 
                'cod' : '2003',
                'delete_count' : f'{delete_pages}',
                }
        return {
            'message' : f'Страницы удалились в количестве {delete_pages}, а сама книга нет',
            'cod' : '2002',
            'delete_count' : f'{delete_pages}',
            }
    
    except Exception as e:
        """Ошибки pyMongo"""
        return {'message': f'Ошибка базы данных: {str(e)}', 'cod': '2004'}
    

class BookGetPage(BaseModel):
    page: str
    book_id : str
@app.post('/get_page/')
async def get_page(
    metadata: BookGetPage,
    repo: BookRepository = Depends(get_book_repository),
    ):
    try:
        page = await repo.get_page(metadata.book_id, int(metadata.page))
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





