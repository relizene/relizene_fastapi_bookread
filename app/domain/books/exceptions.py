class BookError(Exception):
    """Базовое исключение домена Books"""
    cod: str = "0000"
    http_status: int = 400
    message: str = "Book error"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.__class__.message
        super().__init__(self.message)


class PdfExctractionFailed(BookError):
    cod = "1006"
    http_status = 200 
    message = "Не удалось извлечь страницы из PDF"

class UploadDbError(BookError):
    cod = "1005"
    http_status = 200
    message = "Внутренняя ошибка базы данных"

class DeleteDbError(BookError):
    cod = "2004"
    http_status = 200
    message = "Ошибка базы данных"

class PageDbError(BookError):
    cod = "3003"
    http_status = 200
    message = "Ошибка базы данных"

class PageNotFound(BookError):
    cod = "3002"
    http_status = 200
    message = "Страница не найдена"