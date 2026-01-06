"""Pytest fixtures for executor tests"""
import pytest
import sys
from pathlib import Path

# Add executor to path
executor_path = Path(__file__).parent.parent
sys.path.insert(0, str(executor_path))

from engine.engine_signal import EngineSignalHub


@pytest.fixture
def engine_signal_hub():
    """Create a fresh EngineSignalHub instance for testing."""
    return EngineSignalHub(enable_logging=False)


@pytest.fixture
def sample_nodes():
    """Sample nodes for testing."""
    return [
        {
            "nodeId": "n1",
            "name": "add",
            "ref": "builtin",
            "input": [{"var": "a"}, {"var": "b"}],
            "output": ["sum"]
        },
        {
            "nodeId": "n2",
            "name": "multiply",
            "ref": "builtin",
            "input": [{"var": "sum"}, {"value": 2}],
            "output": ["result"]
        }
    ]


@pytest.fixture
def sample_connections():
    """Sample connections for testing."""
    return [
        {
            "connectionId": "c1",
            "sourceNodeId": "n1",
            "sourceOutput": "sum",
            "targetNodeId": "n2"
        }
    ]
