"""Pytest configuration and fixtures for the API tests."""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def sample_activities(client):
    """
    Reset the activities database to a known state for each test.
    
    This fixture ensures tests start with the original activities data,
    allowing tests to modify the data without affecting other tests.
    """
    # Get the activities dictionary from the app
    from src.app import activities
    
    # Store original state
    original_state = {
        name: {
            "description": data["description"],
            "schedule": data["schedule"],
            "max_participants": data["max_participants"],
            "participants": data["participants"].copy()  # Make a copy to avoid mutations
        }
        for name, data in activities.items()
    }
    
    yield activities
    
    # Restore original state after test
    activities.clear()
    activities.update(original_state)
