from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import exc
from database import get_db
from models import Genre
from schemas import GenreBase, GenreCreate
from typing import List

router = APIRouter()

@router.get("/genres/", response_model=List[GenreBase])
def get_genres(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = db.query(Genre)

    genres = query.offset(offset).limit(limit).all()
    return genres

@router.post("/genres/", response_model=GenreCreate)
async def create_genre(genre: GenreCreate, db: Session = Depends(get_db)):
    duplicate_genre = db.query(Genre).filter(Genre.name == genre.name).first()
    if duplicate_genre:
        raise HTTPException(status_code=400, detail="Publisher already exist")

    new_genre = Genre(
       name = genre.name
    )

    db.add(new_genre)
    try:
        db.commit()
        db.refresh(new_genre)
    except exc.SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create genre")

    return new_genre
