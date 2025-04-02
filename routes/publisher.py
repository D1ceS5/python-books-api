from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import exc
from database import get_db
from models import Publisher
from schemas import PublisherBase, PublisherCreate
from typing import List

router = APIRouter()

@router.get("/publishers/", response_model=List[PublisherBase])
def get_publishers(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = db.query(Publisher)

    publishers = query.offset(offset).limit(limit).all()
    return publishers

@router.post("/publishers/", response_model=PublisherCreate)
async def create_publisher(publisher: PublisherCreate, db: Session = Depends(get_db)):
    duplicate_publisher = db.query(Publisher).filter(Publisher.name == publisher.name).first()
    if duplicate_publisher:
        raise HTTPException(status_code=400, detail="Publisher already exist")

    new_publisher = Publisher(
       name = publisher.name
    )

    db.add(new_publisher)
    try:
        db.commit()
        db.refresh(new_publisher)
    except exc.SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create publisher")

    return new_publisher
