import pytest
from executor.engine.node_loader import NodeLoader
from executor.engine.variable_manager import VariableManager
from pathlib import Path
import os

@pytest.fixture
def node_loader():
    # Use the actual builtin path for testing
    return NodeLoader(nodebank_path="nodebank")

def test_add_node(node_loader):
    node = {"nodeId": "n1", "name": "add", "ref": "builtin"}
    func = node_loader.load_node_function(node)
    result = func([10, 5], {})
    assert result == 15.0

def test_subtract_node(node_loader):
    node = {"nodeId": "n1", "name": "subtract", "ref": "builtin"}
    func = node_loader.load_node_function(node)
    result = func([10, 5], {})
    assert result == 5.0

def test_multiply_node(node_loader):
    node = {"nodeId": "n1", "name": "multiply", "ref": "builtin"}
    func = node_loader.load_node_function(node)
    result = func([10, 5], {})
    assert result == 50.0

def test_divide_node(node_loader):
    node = {"nodeId": "n1", "name": "divide", "ref": "builtin"}
    func = node_loader.load_node_function(node)
    result = func([10, 5], {})
    assert result == 2.0
    
    with pytest.raises(ValueError, match="Division by zero"):
        func([10, 0], {})
