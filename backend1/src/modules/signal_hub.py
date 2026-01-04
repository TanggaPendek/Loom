class SignalHub:

    def __init__(self):
        self._listeners = {}

    # Register handler for a signal
    def on(self, signal_name: str, handler):
        if signal_name not in self._listeners:
            self._listeners[signal_name] = []
        self._listeners[signal_name].append(handler)

    # Emit signal to all listeners
    def emit(self, signal_name: str, payload=None):
        handlers = self._listeners.get(signal_name, [])
        for handler in handlers:
            handler(payload)

    # Optional: helper to list registered signals
    def registered_signals(self):
        return list(self._listeners.keys())
