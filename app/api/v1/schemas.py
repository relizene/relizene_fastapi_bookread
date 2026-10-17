from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field, field_validator
from bson import ObjectId
from bson.errors import InvalidId



#---------------Базовые коды для ответов-----------------------
class ResponseCode(StrEnum):
    #uplooad
    BOOK_SAVED = "1001"
    UPLOAD_DB_ERROR = "1005"
    PDF_EXCTRACTION_FAILED = "1006"

    #delete
    BOOK_DELETED = "2001"
    PAGES_DELETED_COUNT_MISMATCH = "2002"
    PAGES_DELETED_BOOK_NOT_FOUND = "2003"
    DELETE_DB_ERROR = "2004"

    #get_page
    PAGE_FOUND = "3001"
    PAGE_NOT_FOUND = "3002"
    PAGE_DB_ERROR = "3003"


#--------------------Базовые методы отправки ответов в словарях
class BookUploadResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message: str
    cod: ResponseCode
    book_id: str | None = None
    saved_pages: str | None = None

class DeleteBookResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message: str 
    cod: ResponseCode
    delete_count: str | None = None

class BookPageResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message: str | None = None
    cod: ResponseCode
    page_number: int | None = None
    content: str | None = None

#----------------------Входящие схемы-------------------


class BookCreateRequests(BaseModel):
    book_name: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)

class BookDeleteRequests(BaseModel):
    id: str
    pages: int = Field(ge=0)

    @field_validator("id")
    @classmethod
    def _validate_object_id(cls, v: str) -> str:
        if not ObjectId.is_valid(v):
            raise ValueError(f"{v} is not valid ObjectId")
        return v

class BookPageRequests(BaseModel):
    book_id: str
    page: int = Field(ge=1)


    @field_validator("book_id")
    @classmethod
    def _validate_object_id(cls, v: str) -> str:
        if not ObjectId.is_valid(v):
            raise ValueError(f"{v} is not valid ObjectId")
        return v
    