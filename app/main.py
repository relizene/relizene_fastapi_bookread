from bson import ObjectId
from fastapi import FastAPI
from pydantic import  BaseModel
import uvicorn
import asyncio
from contextlib import asynccontextmanager

from app.infractructure.pdf.parser import pdf_formater
from app.infractructure.db import mongo



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
async def upload_books(metadata: BookModels) :
    """Загрузка страницы в базу данных. Приходит данные в формате base64. Модуль pdf форматер переводит его
    в пдф и с помощью модуля pymypdf постранично сохраняет его"""
    
    id_back = None
    try:     
        data_for_books_collection = {'book_name' : metadata.book_name,}
        insert_book_result = await mongo.db.book.insert_one(data_for_books_collection)
        id_back = insert_book_result.inserted_id
        books_content = await asyncio.get_event_loop().run_in_executor(
            None,
            pdf_formater,
            metadata.content,
            metadata.book_name,
            id_back
        )
        if books_content:
            insert_result = await mongo.db.pages.insert_many(books_content)
            return {
                'message' : 'Книга сохранена', 
                'сохраненные страницы' : f'{len(insert_result.inserted_ids)} ',
                'id_книги' : str(id_back),
                'cod' : '1001'
                    }
        else:
            await mongo.db.book.delete_one({'_id' : id_back})
            return {'message': 'Не удалось извлечь страницы из PDF', 'cod': '1006'}
    
    except Exception as r:
        """Любая ошибка"""
        if id_back is not None:
            await mongo.db.book.delete_one({'_id' : id_back})
        return {'message': f' Внутреняя Ошибка базы данных: {str(r)}', 'cod': '1005'}
    
    

class BookDeleteModels(BaseModel):
    id : str
    pages : str
@app.post('/books-delete/')
async def delete_books(metadata: BookDeleteModels):
    """Функция для удаления страниц книги и """
    try:
        delete_for_pages = await mongo.db.pages.delete_many({'book_id' : ObjectId(metadata.id)})
        if delete_for_pages.deleted_count == int(metadata.pages):
            delete_books_count = await mongo.db.book.delete_one({'_id' : ObjectId(metadata.id)})
            if delete_books_count.deleted_count == 1:
                return {'message' : f'Книга удалена, удаленных страниц {delete_for_pages.deleted_count}', 'cod' : '2001'}
            return {
                'message' : f'Книга не удалена, но страницы удалены, удаленных страниц {delete_for_pages.deleted_count}', 
                'cod' : '2003',
                'delete_count' : f'{delete_for_pages.deleted_count}',
                }
        return {
            'message' : f'Страницы удалились в количестве {delete_for_pages.deleted_count}, а сама книга нет',
            'cod' : '2002',
            'delete_count' : f'{delete_for_pages.deleted_count}',
            }
    
    except Exception as e:
        """Ошибки pyMongo"""
        return {'message': f'Ошибка базы данных: {str(e)}', 'cod': '2004'}
    

class BookGetPage(BaseModel):
    page: str
    book_id : str
@app.post('/get_page/')
async def get_page(metadata: BookGetPage):
    try:
        page = await mongo.db.pages.find_one({'book_id' : ObjectId(metadata.book_id), 'page' : int(metadata.page)})
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





