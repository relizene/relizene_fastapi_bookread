import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.books.exceptions import BookError




logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BookError)
    async def book_error_handlers(request: Request, exc: BookError) -> JSONResponse:
        logger.warning(
            "Domain errors %s on %s %s: %s",
            exc.cod,
            request.method,
            request.url.path,
            exc.message
        )
        return JSONResponse(
            status_code=exc.http_status,
            content={"message":exc.message, "cod": exc.cod}
        )
    