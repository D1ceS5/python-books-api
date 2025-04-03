from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest
from models import Borrow, Return, Book, Author, Publisher, Genre

TEST_AUTHOR = {
    "name": "Test Author",
    "birth_date": datetime(2000,1,1,1)
}

TEST_PUBLISHER = {
    "name": "Test Publisher"
}

TEST_BOOK = {
    "title": "Test Book",
    "isbn": "978-3-16-148410-0",
    "publish_date": datetime(2000,1,1,1),
    "author_id": 1,
    "publisher_id": 1,
}

TEST_BORROW = {
    "book_id": 1,
    "user_id": 1,
    "is_done": False
}

TEST_RETURN = {
    "book_id": 1,
    "user_id": 1
}

@pytest.fixture(autouse=True)
def setup_db(db: Session):
    """Setup test data for all tests"""
    db.add(Author(**TEST_AUTHOR))
    db.add(Publisher(**TEST_PUBLISHER))
    db.add(Book(id=1, **{**TEST_BOOK, "publish_date": datetime(2000, 1, 1, 1, tzinfo=timezone.utc)}))
    db.commit()

def test_create_borrow_success(client: TestClient, db: Session):
    response = client.post("/api/borrow/", json=TEST_BORROW)
    assert response.status_code == 200
    data = response.json()
    assert data["book_id"] == TEST_BORROW["book_id"]
    assert data["user_id"] == TEST_BORROW["user_id"]
    assert data["is_done"] is False

    borrow = db.query(Borrow).first()
    assert borrow is not None
    assert borrow.book_id == TEST_BORROW["book_id"]
    assert borrow.user_id == TEST_BORROW["user_id"]

def test_create_borrow_book_already_borrowed(client: TestClient, db: Session):
    db.add(Borrow(**TEST_BORROW))
    db.commit()

    response = client.post("/api/borrow/", json=TEST_BORROW)
    assert response.status_code == 400
    assert "Book already borrowed" in response.json()["detail"]

def test_create_borrow_user_limit_reached(client: TestClient, db: Session):
    for i in range(1, 4):
        db.add(Book(**{**TEST_BOOK, "title": f"Book {i}"}))
        db.add(Borrow(book_id=i, user_id=1, is_done=False))
    db.commit()

    response = client.post("/api/borrow/", json={"book_id": 4, "user_id": 1, "is_done": False})
    print(response.json())
    assert response.status_code == 400
    assert "already borrowed too much books" in response.json()["detail"]

def test_create_borrow_nonexistent_book(client: TestClient):
    response = client.post("/api/borrow/", json={"book_id": 999, "user_id": 1, "is_done": False})
    assert response.status_code == 404
    assert "Book not found" in response.json()["detail"]


def test_create_return_success(client: TestClient, db: Session):
    db.add(Borrow(**TEST_BORROW))
    db.commit()

    response = client.post("/api/return/", json=TEST_RETURN)
    assert response.status_code == 200
    data = response.json()
    assert data["book_id"] == TEST_RETURN["book_id"]
    assert data["user_id"] == TEST_RETURN["user_id"]

    borrow = db.query(Borrow).filter_by(book_id=1, user_id=1).first()
    assert borrow.is_done is True
    return_record = db.query(Return).first()
    assert return_record is not None

def test_create_return_no_active_borrow(client: TestClient):
    response = client.post("/api/return/", json=TEST_RETURN)
    assert response.status_code == 404
    assert "Borrow with for this book and user not found" in response.json()["detail"]


def test_create_return_nonexistent_book(client: TestClient):
    response = client.post("/api/return/", json={"book_id": 999, "user_id": 1})
    assert response.status_code == 404
    assert "Borrow with for this book and user not found" in response.json()["detail"]
