from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import exc
from database import get_db
from models import Borrow, Return
from schemas import BorrowCreate, ReturnCreate

router = APIRouter()

MAX_BORROW_COUNT = 3

@router.post("/borrow/", response_model=BorrowCreate)
async def create_genre(borrow: BorrowCreate, db: Session = Depends(get_db)):

    same_book_borrow = db.query(Borrow).filter(Borrow.book_id == borrow.book_id).first()

    if same_book_borrow and not same_book_borrow.is_done:
        raise HTTPException(status_code=400, detail="Book already borrowed")

    user_borrow_count = db.query(Borrow).filter(Borrow.user_id == borrow.user_id).count()
    if user_borrow_count >= MAX_BORROW_COUNT:
        raise HTTPException(status_code=400, detail="User already borrowed too much books")

    new_borrow = Borrow(
       book_id = borrow.book_id,
       user_id = borrow.user_id,
       is_done = False
    )

    db.add(new_borrow)
    try:
        db.commit()
        db.refresh(new_borrow)
    except exc.SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create borrow")

    return new_borrow

@router.post("/return/", response_model=ReturnCreate)
async def create_genre(returnBook: ReturnCreate, db: Session = Depends(get_db)):
    borrow = db.query(Borrow).filter(Borrow.user_id == returnBook.user_id and Borrow.book_id == returnBook.book_id).first()

    if not borrow:
        raise HTTPException(status_code=400, detail="Borrow with for this book and user not found")

    new_return = Return(book_id = returnBook.book_id, user_id = returnBook.user_id)

    borrow.is_done = True
    db.add(new_return)

    try:
        db.commit()
        db.refresh(new_return)
        db.refresh(borrow)
    except exc.SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create borrow")

    return new_return
