import subprocess
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

class VenvManager:
    """
    Manages project-local virtual environments for isolated execution.
    """

    def __init__(self, project_path: Path):
        self.project_path = project_path.resolve()
        self.venv_path = self.project_path / "venv"
        self.python_executable = self.venv_path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

        # Load project-specific .env if it exists
        project_env = self.project_path / ".env"
        if project_env.exists():
            load_dotenv(project_env)
        else:
            print(f"[VenvManager] No project .env found, using defaults.")

    def create_venv(self):
        if not self.venv_path.exists():
            print(f"[VenvManager] Creating virtual environment at {self.venv_path}")
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], check=True)
        else:
            print(f"[VenvManager] Virtual environment already exists at {self.venv_path}")

    def install_requirements(self):
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            print(f"[VenvManager] Installing project dependencies from {req_file}")
            subprocess.run([str(self.python_executable), "-m", "pip", "install", "-r", str(req_file)], check=True)
        else:
            print(f"[VenvManager] No requirements.txt found, skipping installation")

    def run_in_venv(self, script_path: Path, args=None):
        """Run a script inside the project venv"""
        if args is None:
            args = []
        if not self.venv_path.exists():
            raise RuntimeError(f"Venv not found at {self.venv_path}. Please create it first.")
        cmd = [str(self.python_executable), str(script_path)] + args
        subprocess.run(cmd, check=True)

    def get_python(self):
        """Return the path to the python executable in this venv"""
        return self.python_executable



#UNTESTED