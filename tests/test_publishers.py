import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models import Publisher

TEST_PUBLISHER = {"name": "Penguin Books"}
DUPLICATE_PUBLISHER = {"name": "Duplicate Publisher"}


def test_get_publishers_empty(client: TestClient):
    response = client.get("/api/publishers/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_publishers_with_data(client: TestClient, db: Session):
    db.add(Publisher(name=TEST_PUBLISHER["name"]))
    db.commit()

    response = client.get("/api/publishers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == TEST_PUBLISHER["name"]


@pytest.mark.parametrize("params,expected_count", [
    ({"limit": 1, "offset": 0}, 1),
    ({"limit": 10, "offset": 2}, 0),
    ({"limit": 100, "offset": 0}, 2),
])
def test_get_publishers_pagination(client: TestClient, db: Session, params, expected_count):
    db.add_all([
        Publisher(name="Publisher 1"),
        Publisher(name="Publisher 2")
    ])
    db.commit()

    response = client.get("/api/publishers/", params=params)
    assert response.status_code == 200
    assert len(response.json()) == expected_count


def test_create_publisher_success(client: TestClient, db: Session):
    response = client.post("/api/publishers/", json=TEST_PUBLISHER)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == TEST_PUBLISHER["name"]

    publisher = db.query(Publisher).first()
    assert publisher is not None
    assert publisher.name == TEST_PUBLISHER["name"]


def test_create_duplicate_publisher(client: TestClient, db: Session):
    client.post("/api/publishers/", json=DUPLICATE_PUBLISHER)

    response = client.post("/api/publishers/", json=DUPLICATE_PUBLISHER)
    assert response.status_code == 400
    assert "Publisher already exist" in response.json()["detail"]
