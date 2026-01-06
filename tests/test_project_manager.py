import pytest
import json
import shutil
from pathlib import Path
from backend.src.modules.project_manager import ProjectManager
from backend.src.modules.signal_hub import SignalHub

@pytest.fixture
def temp_userdata(tmp_path):
    d = tmp_path / "userdata"
    d.mkdir()
    return d

@pytest.fixture
def signal_hub():
    return SignalHub()

def test_project_init_signals(temp_userdata, signal_hub):
    pm = ProjectManager(base_path=temp_userdata, signal_hub=signal_hub)
    
    received = []
    signal_hub.on("file_save", lambda p: received.append(("save", p["path"])))
    signal_hub.on("project_init", lambda p: received.append(("init", p["projectName"])))
    
    pm.init_project("TestProj")
    
    assert any(r[0] == "save" for r in received)
    assert any(r[0] == "init" for r in received)

def test_project_update_signals(temp_userdata, signal_hub):
    pm = ProjectManager(base_path=temp_userdata, signal_hub=signal_hub)
    pm.init_project("TestProj")
    
    received = []
    signal_hub.on("file_loaded", lambda p: received.append(("loaded", p["path"])))
    signal_hub.on("file_save", lambda p: received.append(("save", p["path"])))
    
    pm.update_project("TestProj", project_updates={"description": "New Desc"})
    
    assert any(r[0] == "loaded" for r in received)
    assert any(r[0] == "save" for r in received)
