import datetime

from models import Borrow, Return

mock_date = datetime.datetime(2024, 1, 1,).date()


def test_get_books_empty(client):
    response = client.get("/api/books")
    assert response.status_code == 200
    assert response.json() == []

def test_create_book(client, create_author, create_genre):
    author = create_author()
    genre = create_genre()

    book_data = {
        "title": "New Book",
        "isbn": "85-0608-47-6",
        "publish_date": mock_date,
        "author_id": author.id,
        "genre_ids": [genre.id]
    }

    response = client.post("/api/books/", json=book_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Book"
    assert data["isbn"] == "9781234567890"
    assert data["author_id"] == author.id

def test_get_book_history(client, create_book, test_db):
    book = create_book()

    borrow = Borrow(book_id=book.id, created_at=mock_date, user_id=1)
    return_record = Return(book_id=book.id, created_at=mock_date, user_id=1)

    test_db.add_all([borrow, return_record])
    test_db.commit()

    response = client.get(f"/api/books/{book.id}/history")
    assert response.status_code == 200
    data = response.json()
    assert len(data["borrows"]) == 1
    assert len(data["returns"]) == 1
    assert data["borrows"][0]["created_at"] == mock_date
    assert data["returns"][0]["created_at"] == mock_date
