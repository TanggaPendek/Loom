"""Pytest fixtures for backend tests"""
import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from src.modules.signal_hub import SignalHub


@pytest.fixture
def signal_hub():
    """Create a fresh SignalHub instance for testing."""
    return SignalHub(enable_logging=False)


@pytest.fixture
def mock_project_payload():
    """Sample project payload for testing."""
    return {
        "projectName": "TestProject",
        "description": "Test project description",
        "author": "Test Author"
    }


@pytest.fixture
def mock_node_payload():
    """Sample node payload for testing."""
    return {
        "nodeId": "test_node_1",
        "name": "TestNode",
        "ref": "builtin",
        "metadata": {
            "description": "Test node"
        }
    }
