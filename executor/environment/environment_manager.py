import os
import sys
import subprocess
import venv

class EnvironmentManager:
    def __init__(self, project_path):
        self.project_path = project_path
        self.venv_path = os.path.join(project_path, "venv")
        self.python_executable = self._get_python_executable()

    def _get_python_executable(self):
        """Determine the correct python path inside the venv."""
        if os.name == "nt":  # Windows
            return os.path.join(self.venv_path, "Scripts", "python.exe")
        else:  # Linux / macOS
            return os.path.join(self.venv_path, "bin", "python")

    def create_if_missing(self):
        """Create the virtual environment if it does not exist."""
        if not os.path.exists(self.venv_path):
            print(f"[EnvironmentManager] Creating venv at {self.venv_path}")
            venv.create(self.venv_path, with_pip=True)
        else:
            print(f"[EnvironmentManager] Venv already exists at {self.venv_path}")

    def is_valid(self):
        """Check if the venv exists and the python executable is present."""
        valid = os.path.exists(self.venv_path) and os.path.exists(self.python_executable)
        print(f"[EnvironmentManager] Venv valid: {valid}")
        return valid

    def install_dependencies(self, requirements_file=None):
        """Install dependencies into the venv."""
        if requirements_file is None:
            requirements_file = os.path.join(self.project_path, "requirements.txt")

        if os.path.exists(requirements_file):
            print(f"[EnvironmentManager] Installing dependencies from {requirements_file}")
            subprocess.check_call([self.python_executable, "-m", "pip", "install", "-r", requirements_file])
        else:
            print(f"[EnvironmentManager] No requirements.txt found at {requirements_file}")
