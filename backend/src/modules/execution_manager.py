# backend/src/modules/execution_manager.py
class ExecutionManager:
    """
    Backend Execution Coordinator
    
    Coordinates execution requests and forwards them to the executor engine.
    Manages execution state and listens to engine feedback signals.
    """
    
    def __init__(self, signal_hub):
        self.signal_hub = signal_hub
        self.running = False
        self.current_run_id = None

        # === Subscribe to Request Signals ===
        signal_hub.on("engine_run_request", self.on_run_request)
        signal_hub.on("engine_stop_request", self.on_stop_request)

        # === Subscribe to Engine Feedback Signals ===
        # (These would come from executor if integrated)
        signal_hub.on("engine_finished", self.on_engine_finished)
        signal_hub.on("engine_error", self.on_engine_error)
        signal_hub.on("engine_progress", self.on_engine_progress)

    def on_run_request(self, payload):
        """Handle execution run request."""
        if self.running:
            self.signal_hub.emit("execution_rejected", {"reason": "already_running"})
            return
        
        self.running = True
        self.current_run_id = payload.get("run_id") if payload else None
        
        # Emit coordination signals
        self.signal_hub.emit("execution_started", payload)
        self.signal_hub.emit("initialization_started", {
            "run_id": self.current_run_id,
            "phase": "starting"
        })
        
        # Forward to engine
        self.signal_hub.emit("engine_run", payload)

    def on_stop_request(self, payload=None):
        """Handle execution stop request."""
        if self.running:
            self.signal_hub.emit("engine_stop")

    def on_engine_progress(self, payload):
        """Forward engine progress to execution progress."""
        self.signal_hub.emit("execution_progress", payload)
        
        # If this is initialization progress, also emit initialization_progress
        if payload and payload.get("phase") == "initialization":
            self.signal_hub.emit("initialization_progress", payload)

    def on_engine_finished(self, payload=None):
        """Handle engine completion."""
        self.running = False
        self.current_run_id = None
        
        # Emit completion signal if initialization phase just finished
        if payload and payload.get("phase") == "initialization":
            self.signal_hub.emit("initialization_completed", payload)
        
        self.signal_hub.emit("execution_finished", payload)

    def on_engine_error(self, payload):
        """Handle engine error."""
        self.running = False
        self.current_run_id = None
        self.signal_hub.emit("execution_error", payload)

