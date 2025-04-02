from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, exc
from database import get_db
from models import Book, Author, Genre, Borrow, Return
from schemas import BookResponse, BookCreate, BookHistoryResponse
from typing import List, Optional

router = APIRouter()

@router.get("/books", response_model=List[BookResponse])
def get_books(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: Optional[str] = Query(None, pattern="^(title|publish_date|author)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
):
    query = db.query(Book).join(Author)

    if sort_by:
        if sort_by == "author":
            order_by_column = Author.name
        else:
            order_by_column = getattr(Book, sort_by)

        query = query.order_by(desc(order_by_column) if order == "desc" else asc(order_by_column))

    books = query.offset(offset).limit(limit).all()
    return books

@router.post("/books/", response_model=BookCreate)
async def create_book(book: BookCreate, db: Session = Depends(get_db)):
    author = db.query(Author).filter(Author.id == book.author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    genres = db.query(Genre).filter(Genre.id.in_(book.genre_ids)).all()
    if len(genres) != len(book.genre_ids):
        raise HTTPException(status_code=404, detail="One or more genres not found")

    new_book = Book(
        title=book.title,
        isbn=book.isbn,
        publish_date=book.publish_date,
        publisher_id=book.publisher_id,
        author_id=book.author_id,
        genres=genres
    )

    db.add(new_book)
    try:
        db.commit()
        db.refresh(new_book)
    except exc.SQLAlchemyError as e:
        db.rollback()
        print(e._message())
        raise HTTPException(status_code=500, detail="Failed to create book")

    return new_book



@router.get("/books/{book_id}/history", response_model=BookHistoryResponse)
def get_book_history(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    borrows = db.query(Borrow).filter(Borrow.book_id == book_id).all()
    returns = db.query(Return).filter(Return.book_id == book_id).all()

    return BookHistoryResponse(borrows=borrows, returns=returns)

