import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models import Genre

TEST_GENRE = {"name": "Fantasy"}
DUPLICATE_GENRE = {"name": "Duplicate Genre"}


def test_get_genre_empty(client: TestClient):
    response = client.get("/api/genres/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_genres_with_data(client: TestClient, db: Session):
    db.add(Genre(name=TEST_GENRE["name"]))
    db.commit()

    response = client.get("/api/genres/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == TEST_GENRE["name"]


@pytest.mark.parametrize("params,expected_count", [
    ({"limit": 1, "offset": 0}, 1),
    ({"limit": 10, "offset": 2}, 0),
    ({"limit": 100, "offset": 0}, 2),
])
def test_get_genres_pagination(client: TestClient, db: Session, params, expected_count):
    db.add_all([
        Genre(name="Genre 1"),
        Genre(name="Genre 2")
    ])
    db.commit()

    response = client.get("/api/genres/", params=params)
    assert response.status_code == 200
    assert len(response.json()) == expected_count


def test_create_publisher_success(client: TestClient, db: Session):
    response = client.post("/api/genres/", json=TEST_GENRE)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == TEST_GENRE["name"]

    genre = db.query(Genre).first()
    assert genre is not None
    assert genre.name == TEST_GENRE["name"]


def test_create_duplicate_publisher(client: TestClient, db: Session):
    client.post("/api/genres/", json=DUPLICATE_GENRE)

    response = client.post("/api/genres/", json=DUPLICATE_GENRE)
    assert response.status_code == 400
    assert "Publisher already exist" in response.json()["detail"]
