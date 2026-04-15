"""Pytest configuration and fixtures for the API tests."""

import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from src.app import app
from src.storage import DataStore


@pytest.fixture
def test_data_dir(tmp_path):
    """Create a temporary directory for test data files."""
    return tmp_path


@pytest.fixture
def test_datastore(test_data_dir):
    """Provide a fresh DataStore instance for each test using a temporary data file."""
    test_file = test_data_dir / "test_activities.json"
    datastore = DataStore(data_file=str(test_file))
    return datastore


@pytest.fixture
def client(monkeypatch, test_datastore):
    """
    Provide a test client for the FastAPI application with isolated data storage.
    
    This fixture replaces the app's datastore with a test-specific instance
    that uses a temporary JSON file, ensuring test isolation.
    """
    # Replace the app's datastore with our test datastore
    monkeypatch.setattr("src.app.datastore", test_datastore)
    
    return TestClient(app)


@pytest.fixture
def sample_activities(client):
    """
    Provide access to the activities for verification within tests.
    
    Uses the test datastore that's already isolated for this test.
    """
    return client  # Return the client; tests can call client.get("/activities")

