import pytest
import json
from pathlib import Path
from backend.src.modules.node_manager import NodeManager
from backend.src.modules.signal_hub import SignalHub

@pytest.fixture
def temp_nodebank(tmp_path):
    custom = tmp_path / "custom"
    custom.mkdir()
    index = tmp_path / "nodeindex.json"
    return custom, index

@pytest.fixture
def signal_hub():
    return SignalHub()

def test_node_add(temp_nodebank, signal_hub):
    custom_path, index_path = temp_nodebank
    nm = NodeManager(base_path=custom_path, signal_hub=signal_hub)
    
    received = []
    signal_hub.on("node_add", lambda p: received.append(p))
    
    node_data = {
        "nodeId": "test_node",
        "name": "test_node",
        "function_code": "def test_node(): pass"
    }
    
    nm.add_node(node_data, index_path)
    
    assert (custom_path / "test_node.py").exists()
    assert (custom_path / "test_node.json").exists()
    assert len(received) == 1
    assert received[0]["nodeId"] == "test_node"

def test_node_update(temp_nodebank, signal_hub):
    custom_path, index_path = temp_nodebank
    nm = NodeManager(base_path=custom_path, signal_hub=signal_hub)
    
    node_data = {
        "nodeId": "test_node",
        "name": "test_node",
        "function_code": "def test_node(): pass"
    }
    nm.add_node(node_data, index_path)
    
    received = []
    signal_hub.on("node_update", lambda p: received.append(p))
    
    nm.update_node({"nodeId": "test_node", "name": "updated_name"}, index_path)
    
    assert len(received) == 1
    assert received[0]["updates"]["name"] == "updated_name"

def test_node_delete(temp_nodebank, signal_hub):
    custom_path, index_path = temp_nodebank
    nm = NodeManager(base_path=custom_path, signal_hub=signal_hub)
    
    node_data = {
        "nodeId": "test_node",
        "name": "test_node",
        "function_code": "def test_node(): pass"
    }
    nm.add_node(node_data, index_path)
    
    received = []
    signal_hub.on("node_delete", lambda p: received.append(p))
    
    nm.delete_node("test_node", index_path)
    
    assert not (custom_path / "test_node.json").exists()
    assert len(received) == 1
    assert received[0]["nodeId"] == "test_node"
