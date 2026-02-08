"""Pytest configuration and fixtures for the app tests."""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to their initial state after each test."""
    from app import activities
    
    # Store original state
    original_state = {
        key: {"participants": value["participants"].copy()} 
        for key, value in activities.items()
    }
    
    yield
    
    # Restore original state
    for key, value in activities.items():
        value["participants"] = original_state[key]["participants"]
