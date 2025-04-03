from datetime import datetime,timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models import Author, Publisher, Book


def next_year_utc_datetime() -> str:
    """Returns UTC datetime for Jan 1 of next year at 1:00 AM in 'YYYY-MM-DDTHH:MM:SSZ' format"""
    now = datetime.now(timezone.utc)
    next_year = now.year + 1
    next_year_date = datetime(next_year, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
    return next_year_date.isoformat(timespec="seconds").replace("+00:00", "Z")

TEST_VALID_AUTHOR = {
    "name": "Test Author",
    "birth_date": "2000-01-01T01:00:00Z"
}

TEST_DUPLICATE_AUTHOR = {
    "name": "Duplicate Author",
    "birth_date": "2000-01-01T01:00:00Z"
}

TEST_INCORRECT_AUTHOR = {
    "name": "Incorrect Author",
    "birth_date": next_year_utc_datetime()
}

TEST_PUBLISHER = {
    "name": "Test Publisher",
}

TEST_BOOK = {
    "title": "Test Book",
    "isbn": "978-3-16-148410-0",
    "publish_date": datetime(2000,1,1,1),
    "author_id": 1,
    "publisher_id": 1,
    "genre_ids": [1]
}

def test_create_author_success(client: TestClient, db: Session):
    response = client.post("/api/author/", json=TEST_VALID_AUTHOR)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == TEST_VALID_AUTHOR["name"]
    assert data["birth_date"] == TEST_VALID_AUTHOR["birth_date"]

    author = db.query(Author).first()
    assert author is not None
    assert author.name == TEST_VALID_AUTHOR["name"]
    assert author.birth_date.isoformat() + "Z" == TEST_VALID_AUTHOR["birth_date"]

def test_create_duplicate_author(client: TestClient, db: Session):
    client.post("/api/author/", json=TEST_DUPLICATE_AUTHOR)

    response = client.post("/api/author/", json=TEST_DUPLICATE_AUTHOR)
    assert response.status_code == 400
    assert "Such author already exist" in response.json()["detail"]

def test_create_invalid_author(client: TestClient, db: Session):
    response = client.post("/api/author/", json=TEST_INCORRECT_AUTHOR)
    assert response.status_code == 422
    assert "Value error, Birth date must be in the past." in response.json()["detail"][0]["msg"]

def test_get_author_books(client: TestClient, db: Session):
    db.add(Author(name=TEST_VALID_AUTHOR["name"], birth_date = datetime(2000,1,1)))
    db.add(Publisher(name=TEST_PUBLISHER["name"]))
    db.add(
        Book(
            title = TEST_BOOK["title"],
            isbn = TEST_BOOK["isbn"],
            publish_date = TEST_BOOK["publish_date"],
            author_id = TEST_BOOK["author_id"],
            publisher_id = TEST_BOOK["publisher_id"]
        )
    )
    db.commit()

    response = client.get("/api/author/1/books")
    assert response.status_code == 200
    assert len(response.json()) == 1