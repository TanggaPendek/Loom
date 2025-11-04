import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
LOG_DIR = Path(os.getenv("LOG_DIR", "./logs"))

# Create directories if missing
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

def get_project_file(project_id: str) -> Path:
    return DATA_DIR / f"{project_id}.json"

def get_log_file(name: str = "app.log") -> Path:
    return LOG_DIR / name
