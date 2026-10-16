from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.dependencies import get_book_service
from app.domain.books.service import BookService
from app.api.v1.schemas import ResponseCode, BookPageResponse, DeleteBookREsponse, BookUploadResponse


router = APIRouter(prefix='/books', tags=["books"])

class BookModels(BaseModel):
    book_name: str
    content: str

class BookDeleteModels(BaseModel):
    id: str
    pages: str

class BookGetPage(BaseModel):
    page: str
    book_id: str


@router.post('/upload/', response_model=BookUploadResponse)
async def upload_books(
    metadata: BookModels,
    service: BookService = Depends(get_book_service)
): 
    """Загрузка страницы в базу данных. Приходит данные в формате base64. Модуль pdf форматер переводит его
        в пдф и с помощью модуля pymypdf постранично сохраняет его"""
    try:
        result = await service.upload(metadata.book_name, metadata.content)
        if result["extraction_failed"] == True:
            return BookUploadResponse(
                cod=ResponseCode.PDF_EXCTRACTION_FAILED,
                message="не удалось извлечь стрицы из pdf"
            )
        return BookUploadResponse(
            cod=ResponseCode.BOOK_SAVED,
            message=f'Книга сохранена',
            book_id = result["book_id"],
            saved_pages = f"{result['saved_pages']}"
        )
    except Exception as e:
        return BookUploadResponse(
            cod=ResponseCode.UPLOAD_DB_ERROR,
            message=f"ошибка базы данных {str(e)}"
        )

@router.post('/delete/', response_model=DeleteBookREsponse)
async def delete_books(
    metadata: BookDeleteModels,
    service: BookService = Depends(get_book_service)
):
    """Функция для удаления страниц книги и самой книги"""
    try:
        excpected = int(metadata.pages)
        result = await service.delete(metadata.id, int(metadata.pages))
        deleted_pages = result['deleted_pages']
        if result['book_deleted']:
            return DeleteBookREsponse(
                cod=ResponseCode.BOOK_DELETED,
                message=f'книга удалена, удаленных страниц {deleted_pages}'
            )
        if deleted_pages == excpected:
            return DeleteBookREsponse(
                cod=ResponseCode.PAGES_DELETED_BOOK_NOT_FOUND,
                message=f'книга не удалена, удаленных страниц {deleted_pages}',
                delete_count=f'{deleted_pages}'
            )
        return DeleteBookREsponse(
            cod=ResponseCode.PAGES_DELETED_COUNT_MISMATCH,
            message=f'Страницы удалились в количестве {deleted_pages}, книга тоже не удалилась',
            delete_count=f'{deleted_pages}'
        )
    except Exception as e:
        return DeleteBookREsponse(
            cod=ResponseCode.DELETE_DB_ERROR,
            message=f'ошибка базы данных {str(e)}'
        )

@router.post('/get_page/', response_model=BookPageResponse)
async def get_page(
    metadata: BookGetPage,
    service: BookService = Depends(get_book_service)
):
    try:
        page = await service.get_page(metadata.book_id, int(metadata.page))
        if page:
            return BookPageResponse(
                cod=ResponseCode.PAGE_FOUND,
                page_number=page.get('page'),
                content=page.get('content')
            )
        return BookPageResponse(
            cod=ResponseCode.PAGE_NOT_FOUND,
            message='Страница не найдена'
        )
    except Exception as e:
        """Ошибки pyMongo"""
        return BookPageResponse(
            cod=ResponseCode.PAGE_DB_ERROR,
            message=f'ошибка базы данных: {str(e)}'
        )