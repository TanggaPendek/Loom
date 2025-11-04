import os
import sys

# Step 1: Calculate Loom root relative to this file
current_file = os.path.abspath(__file__)          # e.g., .../executor/environment/test_env_manager.py
loom_root = os.path.abspath(os.path.join(current_file, "../../.."))  # go up 3 levels to Loom root

# Step 2: Add Loom root to sys.path so imports work from anywhere
if loom_root not in sys.path:
    sys.path.insert(0, loom_root)

# Step 3: Import EnvironmentManager
from executor.environment.environment_manager import EnvironmentManager

# Step 4: Set project path (relative to Loom root)
project_path = os.path.join(loom_root, "userdata", "testfolder")

# Step 5: Create EnvironmentManager instance
venv_manager = EnvironmentManager(project_path)

# Step 6: Create venv if missing
venv_manager.create_if_missing()

# Step 7: Validate venv
if venv_manager.is_valid():
    print("[TEST] Venv is valid.")
else:
    print("[TEST] Venv creation failed.")

# Step 8: Optionally install dependencies
venv_manager.install_dependencies()  # will skip if no requirements.txt

# Step 9: Show Python executable
print(f"[TEST] Venv Python executable: {venv_manager.python_executable}")
