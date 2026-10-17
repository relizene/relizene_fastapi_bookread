from fastapi import APIRouter, Depends

from app.core.dependencies import get_book_service
from app.domain.books.exceptions import BookError, DeleteDbError, PageDbError, UploadDbError
from app.domain.books.service import BookService
from app.api.v1.schemas import (
    ResponseCode,
    BookPageResponse, 
    DeleteBookResponse, 
    BookUploadResponse,
    BookCreateRequests,
    BookDeleteRequests,
    BookPageRequests
    )


router = APIRouter(prefix='/books', tags=["books"])


@router.post('/upload/', response_model=BookUploadResponse)
async def upload_books(
    metadata: BookCreateRequests,
    service: BookService = Depends(get_book_service)
): 
    """Загрузка страницы в базу данных. Приходит данные в формате base64. Модуль pdf форматер переводит его
        в пдф и с помощью модуля pymypdf постранично сохраняет его"""
    try:
        result = await service.upload(metadata.book_name, metadata.content)
    except BookError:
        raise
    except Exception as e:
        raise UploadDbError(f"внутренняя ошибка базы данных {str(e)}")
    return BookUploadResponse(
        message="Книга сохранена",
        cod = ResponseCode.BOOK_SAVED,
        book_id=result["book_id"],
        saved_pages= f"{result["saved_pages"]}",
    )

@router.post('/delete/', response_model=DeleteBookResponse)
async def delete_books(
    metadata: BookDeleteRequests,
    service: BookService = Depends(get_book_service)
):
    """Функция для удаления страниц книги и самой книги"""
    try:
        result = await service.delete(metadata.id, metadata.pages)
    except BookError:
        raise
    except Exception as e:
        raise DeleteDbError(f"ошбика базы данных {str(e)}")
    deleted_pages = result["deleted_pages"]
    if result['book_deleted']:
        return DeleteBookResponse(
            message=f'Книга удалена, удаленных страниц {deleted_pages}',
            cod=ResponseCode.BOOK_DELETED,
        )
    if deleted_pages == metadata.pages:
        return DeleteBookResponse(
            message=f'Книга не удалена, но страницы удалены, удаленных страниц {deleted_pages}',
            cod=ResponseCode.PAGES_DELETED_BOOK_NOT_FOUND,
            delete_count=f'{deleted_pages}',
        )
    return DeleteBookResponse(
        message=f'Страницы удалились в количестве {deleted_pages}, а сама книга нет',
        cod=ResponseCode.PAGES_DELETED_COUNT_MISMATCH,
        delete_count=f'{deleted_pages}',
    )

@router.post('/get_page/', response_model=BookPageResponse)
async def get_page(
    metadata: BookPageRequests,
    service: BookService = Depends(get_book_service)
):
    try:
        page = await service.get_page(metadata.book_id, metadata.page)
    except BookError:
        raise
    except Exception as e:
        raise PageDbError(f"ошибка базы данных {str(e)}")
    return BookPageResponse(
        cod = ResponseCode.PAGE_FOUND,
        page_number=page.get("page"),
        content=page.get('content')
    )