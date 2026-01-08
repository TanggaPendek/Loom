import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# ===== Paths =====
ROOT_DIR = Path(__file__).parent.parent.parent
USERDATA_PATH = ROOT_DIR / "userdata"
CURRENT_PATH = USERDATA_PATH / "current.json"

# Load environment variables if any
env_file = ROOT_DIR / ".env"
if env_file.exists():
    load_dotenv(env_file)

# ===== Helper =====
def read_current():
    if not CURRENT_PATH.exists():
        print("[ENGINE] current.json not found")
        return None
    with open(CURRENT_PATH, "r", encoding="utf-8-sig") as f:
        return json.load(f)  # current.json stores a single object now

# ===== Main engine entrypoint =====
def main():
    current = read_current()
    if not current:
        print("[ENGINE] No active project found in current.json")
        sys.exit(1)

    graph_path = Path(current["projectPath"])
    if not graph_path.exists():
        print(f"[ENGINE] Graph file not found: {graph_path}")
        sys.exit(1)

    # Setup venv
    venv = VenvManager(graph_path.parent)  # project folder
    venv.ensure_venv()
    venv.install_requirements()

    # Run the "graph" in the project folder
    print(f"[ENGINE] Running project: {current['projectName']}")
    # For example, here you might run the script that interprets the savefile.json
    script_to_run = Path(__file__).parent / "run_graph.py"  # your executor logic
    venv.run_in_venv(script_to_run, args=[str(graph_path)])

    print("[ENGINE] Execution finished")


if __name__ == "__main__":
    main()
