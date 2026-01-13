import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
USERDATA_PATH = ROOT_DIR / os.getenv("USERDATA_PATH", "userdata")
NODEBANK_PATH = ROOT_DIR / os.getenv("NODEBANK_PATH", "nodebank")
NODE_INDEX_PATH = NODEBANK_PATH / "nodeindex.json"

def init_directories():
    """Ensures necessary folders exist on startup."""
    for folder in ["custom", "builtin"]:
        (NODEBANK_PATH / folder).mkdir(parents=True, exist_ok=True)
    USERDATA_PATH.mkdir(parents=True, exist_ok=True)