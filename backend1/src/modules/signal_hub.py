# modules/signalhub.py

class SignalHub:
    """
    Local/Scoped SignalHub

    Each module can have its own instance.
    Signals are emitted to this hub and handled only by registered listeners.

    === Usage Notes ===
    1. Create an instance in the module:
        signalhub = SignalHub()
    2. Register listeners using `on(signal_name, handler)`:
        signalhub.on("node_add", handle_node_add)
    3. Emit signals using `emit(signal_name, payload)`:
        signalhub.emit("node_add", {"nodeId": "n1", "name": "Node1"})

    === Supported / Recommended Signals ===

    --- Project-level ---
    - "project_init"         : Emitted when a project is initialized
    - "project_update"       : Emitted when a project is updated
    - "project_delete"       : Emitted when a project is deleted
    - "project_index_update" : Emitted when the project index is updated

    --- Node-level ---
    - "node_add"             : Emitted when a node is added
    - "node_update"          : Emitted when a node is updated
    - "node_delete"          : Emitted when a node is deleted

    --- Engine-level ---
    - "engine_run"           : Request engine to start execution
    - "engine_stop"          : Request engine to stop normally
    - "engine_force_stop"    : Immediately stop execution
    - "engine_node_started"  : Fired when a node starts executing
    - "engine_node_finished" : Fired when a node finishes executing
    - "engine_error"         : Fired when a node or engine throws an error
    - "engine_progress"      : Optional: send progress updates (e.g., % complete)

    --- Persistence / File-level ---
    - "file_save"            : Before saving a file (.json or .py)
    - "file_loaded"          : After loading a file
    - "file_error"           : Emitted if a file operation fails

    --- UI / Frontend Feedback ---
    - "validation_error"     : Emitted by validator on invalid payload
    - "toast_message"        : Generic message display in frontend
    - "highlight_node"       : E.g., highlight or select a node in UI
    """

    def __init__(self):
        # dictionary of signal_name -> list of handlers
        self._listeners = {}

    def on(self, signal_name: str, handler):
        """
        Register a handler for a signal.

        Args:
            signal_name (str): Name of the signal.
            handler (callable): Function that takes one argument (payload).
        """
        if signal_name not in self._listeners:
            self._listeners[signal_name] = []
        self._listeners[signal_name].append(handler)

    def emit(self, signal_name: str, payload=None):
        """
        Emit a signal to all registered handlers for that signal.

        Args:
            signal_name (str): Name of the signal.
            payload: Optional data passed to the handler.
        """
        handlers = self._listeners.get(signal_name, [])
        for handler in handlers:
            handler(payload)

    def registered_signals(self):
        """Return list of all signal names registered in this hub."""
        return list(self._listeners.keys())
