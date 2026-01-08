import subprocess
import sys
import threading
from pathlib import Path
from typing import Optional
from .signal_hub import SignalHub
from backend.src.modules.project_manager import ProjectManager


class ExecutionManager:
    """
    Backend Execution Coordinator - CLI Worker

    Spawns engine process per request and streams stdout/stderr.
    Uses current.json to determine the active project automatically.
    """

    def __init__(self, signal_hub: SignalHub):
        self.signal_hub = signal_hub
        self.process: Optional[subprocess.Popen] = None
        self.running = False
        self.current_run_id = None

        # Signals
        signal_hub.on("engine_run_request", self.on_run_request)
        signal_hub.on("engine_stop_request", self.on_stop_request)
        signal_hub.on("engine_force_stop_request", self.on_force_stop_request)

    def on_run_request(self, payload=None):
        if self.running:
            self.signal_hub.emit("execution_rejected", {"reason": "already_running"})
            return

        # Get active project from current.json
        project_manager = ProjectManager()
        current = project_manager.read_current()
        if not current:
            self.signal_hub.emit("execution_error", {"error": "No current project selected"})
            return

        graph_path = Path(current["projectPath"])
        if not graph_path.exists():
            self.signal_hub.emit("execution_error", {"error": f"Graph not found: {graph_path}"})
            return

        self.running = True
        self.current_run_id = current.get("projectId")
        self.signal_hub.emit("execution_started", {"projectId": self.current_run_id})

        # Launch engine process (absolute path from project root)
        project_root = Path(__file__).parent.parent.parent.parent  # go up from backend/src/modules/
        engine_file = project_root / "executor" / "engine" / "main_engine.py"

        if not engine_file.exists():
            self.signal_hub.emit("execution_error", {"error": f"Engine file not found: {engine_file}"})
            self.running = False
            return

        try:
            self.process = subprocess.Popen(
                [sys.executable, str(engine_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except Exception as e:
            self.signal_hub.emit("execution_error", {"error": str(e)})
            self.running = False
            return


        # Start threads to handle output
        threading.Thread(target=self._read_stdout, daemon=True).start()
        threading.Thread(target=self._read_stderr, daemon=True).start()
        threading.Thread(target=self._wait_for_completion, daemon=True).start()

    def on_stop_request(self, payload=None):
        if self.process and self.running:
            self.process.terminate()

    def on_force_stop_request(self, payload=None):
        if self.process and self.running:
            self.process.kill()

    def _read_stdout(self):
        if not self.process or not self.process.stdout:
            return
        for line in self.process.stdout:
            line = line.strip()
            if line:
                self.signal_hub.emit("execution_output", {"line": line})

    def _read_stderr(self):
        if not self.process or not self.process.stderr:
            return
        for line in self.process.stderr:
            line = line.strip()
            if line:
                self.signal_hub.emit("execution_error", {"line": line})

    def _wait_for_completion(self):
        if not self.process:
            return
        self.process.wait()
        exit_code = self.process.returncode
        self.running = False
        self.current_run_id = None
        self.process = None
        self.signal_hub.emit("execution_finished", {"exit_code": exit_code})
