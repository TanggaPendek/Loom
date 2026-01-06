import pytest
import json
from pathlib import Path
from executor.engine.execution_manager import ExecutionManager
from executor.engine.variable_manager import VariableManager
from backend.src.modules.signal_hub import SignalHub

def test_execution_manager_signals():
    nodes = [
        {
            "nodeId": "n1",
            "name": "test_node",
            "ref": "builtin",
            "input": [],
            "output": ["out1"]
        }
    ]
    
    def test_func(inputs, variables):
        return 42
        
    loaded_nodes = {"n1": test_func}
    var_mgr = VariableManager()
    var_mgr.init_variables(nodes)
    connections = []
    signal_hub = SignalHub()
    
    received = []
    signal_hub.on("engine_run", lambda p: received.append("run"))
    signal_hub.on("engine_node_started", lambda p: received.append(("started", p["nodeId"])))
    signal_hub.on("engine_node_finished", lambda p: received.append(("finished", p["nodeId"], p["output"])))
    signal_hub.on("engine_stop", lambda p: received.append("stop"))
    
    exec_mgr = ExecutionManager(
        nodes=nodes,
        loaded_nodes=loaded_nodes,
        variable_manager=var_mgr,
        connections=connections,
        signal_hub=signal_hub
    )
    
    exec_mgr.run_linear()
    
    assert "run" in received
    assert ("started", "n1") in received
    assert ("finished", "n1", 42) in received
    assert "stop" in received
    assert var_mgr.variables["out1"] == 42
