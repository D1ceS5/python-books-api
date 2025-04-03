from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import exc
from sqlalchemy.orm import Session
from database import get_db
from models import Author, Book
from schemas import AuthorCreate, BookResponse

router = APIRouter()

@router.get('/author/{author_id}/books', response_model=List[BookResponse])
def get_author_books(
        author_id: int,
        db: Session = Depends(get_db)
):
    books = db.query(Book).filter(Book.author_id == author_id).all()

    return books

@router.post('/author/', response_model=AuthorCreate)
def create_author(
        author: AuthorCreate,
        db: Session = Depends(get_db)
):
    duplicate_author = db.query(Author).filter(Author.name == author.name).first()

    if duplicate_author:
        raise HTTPException(status_code=400, detail="Such author already exist")

    new_author = Author(name=author.name, birth_date = author.birth_date)

    db.add(new_author)
    try:
        db.commit()
        db.refresh(new_author)
    except exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create book")

    return new_author