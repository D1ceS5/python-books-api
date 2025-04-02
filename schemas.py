from pydantic import BaseModel, field_validator, Field
from typing import List, Optional
from datetime import datetime, timezone


# Genre Schemas
class GenreBase(BaseModel):
    name: str

class GenreCreate(GenreBase):
    pass

class GenreResponse(GenreBase):
    id: int
    class Config:
        from_attributes = True

# Author Schemas
class AuthorBase(BaseModel):
    name: str
    birth_date: datetime

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, value):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        if value >= datetime.now(timezone.utc):
            raise ValueError("Birth date must be in the past.")
        return value

class AuthorCreate(AuthorBase):
    pass

# Book Schemas
class BookBase(BaseModel):
    title: str
    isbn: str
    publish_date: datetime
    author_id: int
    publisher_id: Optional[int]
    genre_ids: List[int] = []

    @field_validator("publish_date")
    @classmethod
    def validate_publish_date(cls, value):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        if value >= datetime.now(timezone.utc):
            raise ValueError("Publish date must be in the past.")
        return value

class BookCreate(BookBase):
    isbn: str = Field(pattern = r'^[0-9]{1,5}-[0-9]{1,7}-[0-9]{1,5}-[0-9X]$')

class BookResponse(BookBase):
    id: int
    author: AuthorBase
    genres: List[GenreResponse] = []
    class Config:
        from_attributes = True

# Borrow Schemas
class BorrowBase(BaseModel):
    user_id: int
    book_id: int
    is_done: bool

class BorrowCreate(BorrowBase):
    pass

class BorrowResponse(BorrowBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# Return Schemas
class ReturnBase(BaseModel):
    user_id: int
    book_id: int

class ReturnCreate(ReturnBase):
    pass

class ReturnResponse(ReturnBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# Publisher Schemas
class PublisherBase(BaseModel):
    name: str

class PublisherCreate(PublisherBase):
    pass

# Book History Schema
class BookHistoryResponse(BaseModel):
    borrows: List[BorrowResponse] = []
    returns: List[ReturnResponse] = []