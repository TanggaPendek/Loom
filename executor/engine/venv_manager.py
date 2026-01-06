# executor/engine/venv_manager.py
import subprocess
import sys
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional
from executor.engine.engine_signal import EngineSignalHub



class VenvManager:
    """
    Manages project-local virtual environments for isolated execution.
    """

    def __init__(self, project_path: Path, signal_hub: Optional[EngineSignalHub] = None):
        """
        Initialize VenvManager.
        
        Args:
            project_path: Path to the project directory
            signal_hub: Optional EngineSignalHub for emitting signals
        """
        self.project_path = project_path.resolve()
        self.venv_path = self.project_path / "venv"
        self.python_executable = self.venv_path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        self.signal_hub = signal_hub

        # Load project-specific .env if it exists
        project_env = self.project_path / ".env"
        if project_env.exists():
            load_dotenv(project_env)
        else:
            print(f"[VenvManager] No project .env found, using defaults.")

    async def ensure_venv_async(self, timeout: int = 300) -> None:
        """
        Ensure virtual environment is ready (create if needed, install requirements).
        
        Args:
            timeout: Timeout in seconds for pip install operations
            
        Raises:
            asyncio.TimeoutError: If operations exceed timeout
            RuntimeError: If venv operations fail
        """
        if self.signal_hub:
            self.signal_hub.emit("venv_check_started", {"path": str(self.venv_path)})
        
        try:
            # Create venv if it doesn't exist
            if not self.venv_path.exists():
                await self._create_venv_async()
            else:
                print(f"[VenvManager] Virtual environment already exists at {self.venv_path}")
            
            # Install requirements
            await asyncio.wait_for(
                self._install_requirements_async(),
                timeout=timeout
            )
            
            if self.signal_hub:
                self.signal_hub.emit("venv_ready", {"path": str(self.venv_path)})
                
        except asyncio.TimeoutError:
            error_msg = f"Venv operations exceeded {timeout}s timeout"
            print(f"[VenvManager ERROR] {error_msg}")
            if self.signal_hub:
                self.signal_hub.emit("venv_error", {
                    "error": error_msg,
                    "stage": "timeout"
                })
            raise
        except Exception as e:
            print(f"[VenvManager ERROR] {e}")
            if self.signal_hub:
                self.signal_hub.emit("venv_error", {
                    "error": str(e),
                    "stage": "general"
                })
            raise

    async def _create_venv_async(self) -> None:
        """Create virtual environment asynchronously."""
        if self.signal_hub:
            self.signal_hub.emit("venv_creation_started", {"path": str(self.venv_path)})
        
        print(f"[VenvManager] Creating virtual environment at {self.venv_path}")
        
        # Run venv creation as subprocess
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "venv", str(self.venv_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = f"Failed to create venv: {stderr.decode()}"
            if self.signal_hub:
                self.signal_hub.emit("venv_error", {
                    "error": error_msg,
                    "stage": "creation"
                })
            raise RuntimeError(error_msg)
        
        if self.signal_hub:
            self.signal_hub.emit("venv_creation_completed", {"path": str(self.venv_path)})

    async def _install_requirements_async(self) -> None:
        """Install requirements asynchronously with progress streaming."""
        req_file = self.project_path / "requirements.txt"
        
        if not req_file.exists():
            print(f"[VenvManager] No requirements.txt found, skipping installation")
            return
        
        if self.signal_hub:
            self.signal_hub.emit("venv_install_started", {"requirements_file": str(req_file)})
        
        print(f"[VenvManager] Installing project dependencies from {req_file}")
        
        # Run pip install as subprocess with streaming output
        process = await asyncio.create_subprocess_exec(
            str(self.python_executable), "-m", "pip", "install", "-r", str(req_file),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        
        # Stream output
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            line_str = line.decode().strip()
            if line_str:
                print(f"[pip] {line_str}")
                if self.signal_hub:
                    self.signal_hub.emit("venv_install_progress", {"line": line_str})
        
        await process.wait()
        
        if process.returncode != 0:
            error_msg = "Failed to install requirements"
            if self.signal_hub:
                self.signal_hub.emit("venv_error", {
                    "error": error_msg,
                    "stage": "install"
                })
            raise RuntimeError(error_msg)
        
        if self.signal_hub:
            self.signal_hub.emit("venv_install_completed", {"requirements_file": str(req_file)})

    def create_venv(self) -> None:
        """Create virtual environment (synchronous wrapper)."""
        if not self.venv_path.exists():
            print(f"[VenvManager] Creating virtual environment at {self.venv_path}")
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], check=True)
        else:
            print(f"[VenvManager] Virtual environment already exists at {self.venv_path}")

    def install_requirements(self) -> None:
        """Install requirements (synchronous wrapper)."""
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            print(f"[VenvManager] Installing project dependencies from {req_file}")
            subprocess.run([str(self.python_executable), "-m", "pip", "install", "-r", str(req_file)], check=True)
        else:
            print(f"[VenvManager] No requirements.txt found, skipping installation")

    def run_in_venv(self, script_path: Path, args=None) -> None:
        """
        Run a script inside the project venv.
        
        Args:
            script_path: Path to script to run
            args: Optional command line arguments
        """
        if args is None:
            args = []
        if not self.venv_path.exists():
            raise RuntimeError(f"Venv not found at {self.venv_path}. Please create it first.")
        cmd = [str(self.python_executable), str(script_path)] + args
        subprocess.run(cmd, check=True)

    def get_python(self) -> Path:
        """
        Return the path to the python executable in this venv.
        
        Returns:
            Path to python executable
        """
        return self.python_executable