from datetime import datetime,timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models import Author, Publisher, Book


def next_year_utc_datetime() -> str:
    """Returns UTC datetime for Jan 1 of next year at 1:00 AM in 'YYYY-MM-DDTHH:MM:SSZ' format"""
    now = datetime.now(timezone.utc)
    next_year = now.year + 1
    next_year_date = datetime(next_year, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
    return next_year_date.isoformat(timespec="seconds").replace("+00:00", "Z")

TEST_AUTHOR = {
    "name": "Test Author",
    "birth_date": "2000-01-01T01:00:00Z"
}

TEST_DUPLICATE_AUTHOR = {
    "name": "Duplicate Author",
    "birth_date": "2000-01-01T01:00:00Z"
}

TEST_PUBLISHER = {
    "name": "Test Publisher",
}

TEST_BOOK = {
    "title": "Test Book",
    "isbn": "123-4-5678-9",
    "publish_date": datetime(2000,1,1,1).isoformat() + "Z",
    "author_id": 1,
    "publisher_id": 1,
}

TEST_INCORRECT_DATE_BOOK = {
    **TEST_BOOK,
    "publish_date": next_year_utc_datetime()
}

TEST_INCORRECT_AUTHOR_BOOK = {
    **TEST_BOOK,
    "author_id": 0
}

TEST_INCORRECT_ISBN_BOOK = {
    **TEST_BOOK,
    "isbn": 'not correct isbn'
}

def test_create_book_success(client: TestClient, db: Session):
    db.add(Author(name=TEST_AUTHOR["name"], birth_date=datetime(2000, 1, 1)))
    db.add(Publisher(name=TEST_PUBLISHER["name"]))
    db.commit()

    response = client.post("/api/books/", json=TEST_BOOK)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == TEST_BOOK["title"]
    assert data["isbn"] == TEST_BOOK["isbn"]
    assert data["publish_date"] == TEST_BOOK["publish_date"]

    book = db.query(Book).first()
    assert book is not None
    assert book.title == TEST_BOOK["title"]
    assert book.isbn == TEST_BOOK["isbn"]
    assert book.publish_date.isoformat() + "Z" == TEST_BOOK["publish_date"]

def test_create_incorrect_author_book(client: TestClient, db: Session):
    response = client.post("/api/books/", json=TEST_INCORRECT_AUTHOR_BOOK)
    assert response.status_code == 404
    assert "Author not found" in response.json()["detail"]

def test_create_incorrect_isbn_book(client: TestClient, db: Session):
    response = client.post("/api/books/", json=TEST_INCORRECT_ISBN_BOOK)
    assert response.status_code == 422
    assert "String should match pattern" in response.json()["detail"][0]["msg"]

def test_create_incorrect_date_book(client: TestClient, db: Session):
    response = client.post("/api/books/", json=TEST_INCORRECT_DATE_BOOK)
    assert response.status_code == 422
    assert "Value error, Publish date must be in the past." in response.json()["detail"][0]["msg"]

@pytest.mark.parametrize("params,expected_count", [
    ({"limit": 1, "offset": 0}, 1),
    ({"limit": 10, "offset": 2}, 0),
    ({"limit": 100, "offset": 0}, 2),
])
def test_get_books_pagination(client: TestClient, db: Session, params, expected_count):
    db.add(Author(name=TEST_AUTHOR["name"], birth_date=datetime(2000, 1, 1)))
    db.add(Publisher(name=TEST_PUBLISHER["name"]))

    db.add_all([
        Book(**{**TEST_BOOK, "title": "Book 1", "publish_date": datetime(2000,1,1,1)}),
        Book(**{**TEST_BOOK, "title": "Book 2", "publish_date": datetime(2000,1,1,1)})
    ])
    db.commit()

    response = client.get("/api/books", params=params)
    assert response.status_code == 200
    assert len(response.json()) == expected_count
