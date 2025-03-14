import pytest
from services import user_service
from db.database import users_db

@pytest.fixture
def setup_users():
    # Clear the users database before each test
    users_db.clear()
    yield

def test_create_user(setup_users):
    # Test creating a new user
    user, error = user_service.create_user(
        username="testuser",
        password="password123",
        email="test@example.com",
        full_name="Test User"
    )
    
    assert error is None
    assert user is not None
    assert user["username"] == "testuser"
    assert user["email"] == "test@example.com"
    assert user["full_name"] == "Test User"
    assert "id" in user
    assert "created_at" in user
    
    # Verify user was added to the database
    assert len(users_db) == 1
    assert users_db[0]["username"] == "testuser"

def test_create_duplicate_user(setup_users):
    # Create first user
    user_service.create_user(
        username="testuser",
        password="password123",
        email="test@example.com"
    )
    
    # Try to create duplicate user
    user, error = user_service.create_user(
        username="testuser",
        password="different",
        email="another@example.com"
    )
    
    assert user is None
    assert error == "Username already exists"
    assert len(users_db) == 1  # No new user added

def test_get_user_by_username(setup_users):
    # Create a user
    created_user, _ = user_service.create_user(
        username="testuser",
        password="password123",
        email="test@example.com",
        full_name="Test User"
    )
    
    # Get user by username
    user = user_service.get_user_by_username("testuser")
    
    assert user is not None
    assert user["id"] == created_user["id"]
    assert user["username"] == "testuser"
    
    # Test non-existent user
    non_existent = user_service.get_user_by_username("nonexistent")
    assert non_existent is None

def test_get_user_by_id(setup_users):
    # Create a user
    created_user, _ = user_service.create_user(
        username="testuser",
        password="password123",
        email="test@example.com",
        full_name="Test User"
    )
    
    # Get user by ID
    user = user_service.get_user_by_id(created_user["id"])
    
    assert user is not None
    assert user["id"] == created_user["id"]
    assert user["username"] == "testuser"
    
    # Test non-existent user
    non_existent = user_service.get_user_by_id("nonexistent-id")
    assert non_existent is None