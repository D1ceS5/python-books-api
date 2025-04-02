# database_test_setup.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from fastapi.testclient import TestClient
from main import app

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def setup_test_db():
    """Fixture to create a new test database session for each test."""
    Base.metadata.create_all(bind=engine)  # Create tables
    db = TestingSessionLocal()
    try:
        yield db  # Provide the session to the test
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)  # Clean up after test

def override_get_db():
    """Override FastAPI's dependency injection to use the test database."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override FastAPI's database dependency
app.dependency_overrides[get_db] = override_get_db

# Create a test client
client = TestClient(app)
