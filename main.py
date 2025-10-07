from bson import ObjectId
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pydantic import  BaseModel
import uvicorn
from pdf import pdf_formater, delete_file
import os


app = FastAPI()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = MongoClient(MONGO_URL)
db = client['book_library']
books_collection = db.book
books_pages = db.pages


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
        id_back = books_collection.insert_one(data_for_books_collection).inserted_id
        books_content = pdf_formater(metadata.content, metadata.book_name, id_back)
        if books_content:
            insert_result = books_pages.insert_many(books_content)
            return {
                'message' : 'Книга сохранена', 
                'сохраненные страницы' : f'{len(insert_result.inserted_ids)} ',
                'id_книги' : str(id_back),
                'cod' : '1001'
                    }
        else:
            books_collection.delete_one({'_id' : id_back})
            return {'message': 'Не удалось извлечь страницы из PDF', 'cod': '1006'}
        
    except PyMongoError as e:
        """Ошибки pyMongo"""
        if id_back is not None:
            books_collection.delete_one({'_id' : id_back})
        return {'message': f'Ошибка базы данных: {str(e)}', 'cod': '1004'}
    
    except Exception as r:
        """Любая ошибка"""
        if id_back is not None:
            books_collection.delete_one({'_id' : id_back})
        return {'message': f' Внутреняя Ошибка базы данных: {str(r)}', 'cod': '1005'}
    
    finally:
        delete_file(metadata.book_name)
    

class BookDeleteModels(BaseModel):
    id : str
    pages : str
@app.post('/books-delete/')
async def delete_books(metadata: BookDeleteModels):
    """Функция для удаления страниц книги и """
    try:
        delete_for_pages = books_pages.delete_many({'book_id' : ObjectId(metadata.id)})
        if delete_for_pages.deleted_count == int(metadata.pages):
            delete_books_count = books_collection.delete_one({'_id' : ObjectId(metadata.id)})
            if delete_books_count.deleted_count == 1:
                return {'message' : f'Книга удалена, удаленных страниц {delete_for_pages.deleted_count}', 'cod' : '2001'}
            return {
                'message' : f'Книга не удалена, но страницы удалены, удаленных страниц {delete_for_pages.deleted_count}', 
                'cod' : '2003',
                }
        return {
            'message' : f'Страницы удалились в количестве {delete_for_pages.deleted_count}, а сама книга нет',
            'cod' : '2002',
            }
    
    except PyMongoError as e:
        """Ошибки pyMongo"""
        return {'message': f'Ошибка базы данных: {str(e)}', 'cod': '2004'}
    

class BookGetPage(BaseModel):
    page: str
    book_id : str
@app.post('/get_page/')
async def get_page(metadata: BookGetPage):
    try:
        page = books_pages.find_one({'book_id' : ObjectId(metadata.book_id), 'page' : int(metadata.page)})
        if page:
            return {
            'page_number' : page.get('page'),
            'cod' : '3001',
            'content' : page.get('content'),
            }
        return {'message' : 'Страница не найдена', 'cod' : '3002'}
    except PyMongoError as e:
        """Ошибки pyMongo"""
        return {'message': f'Ошибка базы данных: {str(e)}', 'cod': '3003'}


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)





