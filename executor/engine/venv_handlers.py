from __future__ import annotations
import subprocess
import sys
import os
import asyncio
from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from executor.engine.engine_signal import EngineSignalHub
    from executor.engine.ws_client import EngineWSClient


class VenvManager:
    def __init__(self, project_path: Path, signal_hub: Optional['EngineSignalHub'] = None,
                 ws_client: Optional['EngineWSClient'] = None):
        self.project_path = project_path.resolve()
        self.venv_path = self.project_path / "venv"
        self.ws_client = ws_client

        if os.name == "nt":
            self.python_executable = self.venv_path / "Scripts" / "python.exe"
        else:
            self.python_executable = self.venv_path / "bin" / "python"

        self.signal_hub = signal_hub

    def get_python(self) -> Path:
        return self.python_executable.resolve()

    async def ensure_venv_async(self, timeout: int = 300) -> None:
        """Creates venv if missing and installs requirements if changed."""
        if not self.venv_path.exists():
            await self._create_venv_async()

        # Always check for requirements updates on bootstrap
        await asyncio.wait_for(self._install_requirements_async(), timeout=timeout)

    async def _create_venv_async(self) -> None:
        if self.signal_hub:
            self.signal_hub.emit("venv_creation_started", {"path": str(self.venv_path)})

        print(f"[ENGINE] Creating venv at {self.venv_path}...")
        sys.stdout.flush()
        if self.ws_client:
            await self.ws_client.send("venv_create", {"path": str(self.venv_path)})

        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "venv", str(self.venv_path)
        )
        await process.wait()
        print(f"[ENGINE] Venv created.")
        sys.stdout.flush()

    async def _install_requirements_async(self) -> None:
        """Installs from requirements.txt if it exists."""
        req_file = self.project_path / "requirements.txt"
        if not req_file.exists():
            return

        if self.signal_hub:
            self.signal_hub.emit("venv_install_started", {"file": str(req_file)})

        print(f"[ENGINE] Installing dependencies from {req_file}...")
        sys.stdout.flush()
        if self.ws_client:
            await self.ws_client.send("venv_install", {"file": str(req_file)})

        process = await asyncio.create_subprocess_exec(
            str(self.get_python()), "-m", "pip", "install", "-r", str(req_file),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )

        while True:
            line = await process.stdout.readline()
            if not line:
                break
            line_str = line.decode().strip()
            if line_str:
                print(f"[ENGINE/pip] {line_str}")
                sys.stdout.flush()
                if self.signal_hub:
                    self.signal_hub.emit("venv_install_progress", {"line": line_str})
                if self.ws_client:
                    await self.ws_client.send("dep_progress", {"line": line_str})

        await process.wait()
        print(f"[ENGINE] Dependencies installed.")
        sys.stdout.flush()