# executor/engine/engine_signal.py
import asyncio
import logging
from typing import Callable, Any, Optional, Dict, List
from datetime import datetime
import inspect

logger = logging.getLogger(__name__)


class EngineSignalHub:
    """
    Executor Engine SignalHub with async/await support
    
    Internal signal system for executor engine coordination. Similar to backend
    SignalHub but focused on engine-specific signals.
    
    === Usage Notes ===
    
    **Basic Sync Usage:**
    ```python
    hub = EngineSignalHub()
    hub.on("node_loaded", lambda payload: print(f"Loaded: {payload}"))
    hub.emit("node_loaded", {"nodeId": "n1"})
    ```
    
    **Async Handler Usage:**
    ```python
    async def async_handler(payload):
        await some_async_operation(payload)
    
    hub.on_async("node_loaded", async_handler)
    await hub.emit_async("node_loaded", {"nodeId": "n1"})
    ```
    
    **Fire-and-Forget Async:**
    ```python
    hub.emit_concurrent("node_loaded", {"nodeId": "n1"})
    # Returns immediately, handlers run in background
    ```
    
    === Executor Engine Signals ===
    
    --- Node Loading ---
    - "nodeloader_started"    : Node loading begins {count}
    - "node_loading"          : Loading specific node {nodeId, name, progress}
    - "node_loaded"           : Node loaded successfully {nodeId, name}
    - "node_load_failed"      : Node load failed {nodeId, error}
    - "nodeloader_completed"  : All nodes loaded {loaded_count, failed_count}
    
    --- Variable Manager ---
    - "varmanager_started"       : Variable initialization begins
    - "varmanager_initialized"   : Initialization complete {variable_count}
    - "variable_set"             : Variable changed {var_name, value}
    
    --- Virtual Environment ---
    - "venv_check_started"       : Checking venv status
    - "venv_creation_started"    : Creating new venv
    - "venv_creation_completed"  : Venv created successfully
    - "venv_install_started"     : Installing dependencies
    - "venv_install_progress"    : Pip install progress {line}
    - "venv_install_completed"   : Dependencies installed
    - "venv_ready"               : Venv ready for use
    - "venv_error"               : Venv operation failed {error, stage}
    
    --- Execution ---
    - "engine_run"               : Engine starting execution {status}
    - "engine_node_started"      : Node execution started {nodeId}
    - "engine_node_finished"     : Node execution finished {nodeId, output}
    - "engine_stop"              : Engine stopping {status}
    - "engine_error"             : Engine error occurred {error}
    - "engine_progress"          : Execution progress {current, total, percent}
    
    --- Error Handling ---
    - "handler_error"            : Signal handler threw exception
    """
    
    def __init__(self, enable_logging: bool = False):
        """
        Initialize EngineSignalHub.
        
        Args:
            enable_logging: If True, log all signal emissions and handler errors
        """
        # Signal name -> list of (handler, metadata) tuples
        self._listeners: Dict[str, List[tuple]] = {}
        # Signal name -> list of (async_handler, metadata) tuples
        self._async_listeners: Dict[str, List[tuple]] = {}
        self._enable_logging = enable_logging
    
    def on(self, signal_name: str, handler: Callable[[Any], None]) -> None:
        """
        Register a synchronous handler for a signal.
        
        Args:
            signal_name: Name of the signal
            handler: Synchronous function that takes one argument (payload)
        """
        if signal_name not in self._listeners:
            self._listeners[signal_name] = []
        
        metadata = {
            "name": handler.__name__ if hasattr(handler, "__name__") else "lambda",
            "registered_at": datetime.utcnow().isoformat()
        }
        self._listeners[signal_name].append((handler, metadata))
        
        if self._enable_logging:
            logger.info(f"[EngineSignalHub] Registered sync handler '{metadata['name']}' for signal '{signal_name}'")
    
    def on_async(self, signal_name: str, async_handler: Callable[[Any], Any]) -> None:
        """
        Register an asynchronous handler for a signal.
        
        Args:
            signal_name: Name of the signal
            async_handler: Async function that takes one argument (payload)
        """
        if not inspect.iscoroutinefunction(async_handler):
            raise ValueError(f"Handler {async_handler} is not an async function. Use on() for sync handlers.")
        
        if signal_name not in self._async_listeners:
            self._async_listeners[signal_name] = []
        
        metadata = {
            "name": async_handler.__name__ if hasattr(async_handler, "__name__") else "async_lambda",
            "registered_at": datetime.utcnow().isoformat()
        }
        self._async_listeners[signal_name].append((async_handler, metadata))
        
        if self._enable_logging:
            logger.info(f"[EngineSignalHub] Registered async handler '{metadata['name']}' for signal '{signal_name}'")
    
    def off(self, signal_name: str, handler: Callable) -> bool:
        """
        Unregister a specific handler from a signal.
        
        Args:
            signal_name: Name of the signal
            handler: The handler to remove
            
        Returns:
            True if handler was found and removed, False otherwise
        """
        # Try sync handlers
        if signal_name in self._listeners:
            original_length = len(self._listeners[signal_name])
            self._listeners[signal_name] = [
                (h, m) for h, m in self._listeners[signal_name] if h != handler
            ]
            if len(self._listeners[signal_name]) < original_length:
                if self._enable_logging:
                    logger.info(f"[EngineSignalHub] Unregistered sync handler from signal '{signal_name}'")
                return True
        
        # Try async handlers
        if signal_name in self._async_listeners:
            original_length = len(self._async_listeners[signal_name])
            self._async_listeners[signal_name] = [
                (h, m) for h, m in self._async_listeners[signal_name] if h != handler
            ]
            if len(self._async_listeners[signal_name]) < original_length:
                if self._enable_logging:
                    logger.info(f"[EngineSignalHub] Unregistered async handler from signal '{signal_name}'")
                return True
        
        return False
    
    def clear(self, signal_name: str) -> None:
        """
        Remove all handlers (sync and async) for a signal.
        
        Args:
            signal_name: Name of the signal to clear
        """
        removed_count = 0
        if signal_name in self._listeners:
            removed_count += len(self._listeners[signal_name])
            del self._listeners[signal_name]
        if signal_name in self._async_listeners:
            removed_count += len(self._async_listeners[signal_name])
            del self._async_listeners[signal_name]
        
        if self._enable_logging and removed_count > 0:
            logger.info(f"[EngineSignalHub] Cleared {removed_count} handlers from signal '{signal_name}'")
    
    def emit(self, signal_name: str, payload: Any = None) -> None:
        """
        Emit a signal to all registered synchronous handlers.
        
        Handlers are executed sequentially. If a handler raises an exception,
        it is caught, logged, and other handlers continue to execute.
        
        Args:
            signal_name: Name of the signal
            payload: Optional data to pass to handlers
        """
        if self._enable_logging:
            logger.debug(f"[EngineSignalHub] Emitting signal '{signal_name}' with payload: {payload}")
        
        handlers = self._listeners.get(signal_name, [])
        for handler, metadata in handlers:
            try:
                handler(payload)
            except Exception as e:
                handler_name = metadata.get("name", "unknown")
                logger.error(f"[EngineSignalHub] Error in sync handler '{handler_name}' for signal '{signal_name}': {e}")
                # Emit handler_error signal (but avoid infinite recursion)
                if signal_name != "handler_error":
                    self.emit("handler_error", {
                        "signal": signal_name,
                        "handler": handler_name,
                        "error": str(e)
                    })
    
    async def emit_async(self, signal_name: str, payload: Any = None) -> None:
        """
        Emit a signal and await all registered handlers (sync and async).
        
        Synchronous handlers are executed first, then async handlers are awaited.
        All async handlers run concurrently via asyncio.gather().
        
        If a handler raises an exception, it is caught, logged, and other handlers
        continue to execute.
        
        Args:
            signal_name: Name of the signal
            payload: Optional data to pass to handlers
        """
        if self._enable_logging:
            logger.debug(f"[EngineSignalHub] Async emitting signal '{signal_name}' with payload: {payload}")
        
        # Execute sync handlers first
        self.emit(signal_name, payload)
        
        # Execute async handlers concurrently
        async_handlers = self._async_listeners.get(signal_name, [])
        if async_handlers:
            async def safe_call(handler, metadata):
                try:
                    await handler(payload)
                except Exception as e:
                    handler_name = metadata.get("name", "unknown")
                    logger.error(f"[EngineSignalHub] Error in async handler '{handler_name}' for signal '{signal_name}': {e}")
                    if signal_name != "handler_error":
                        self.emit("handler_error", {
                            "signal": signal_name,
                            "handler": handler_name,
                            "error": str(e),
                            "async": True
                        })
            
            tasks = [safe_call(handler, metadata) for handler, metadata in async_handlers]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def emit_concurrent(self, signal_name: str, payload: Any = None) -> None:
        """
        Emit a signal and fire async handlers in the background (fire-and-forget).
        
        This is useful when you want to trigger async handlers but don't want to
        await them. The call returns immediately.
        
        Args:
            signal_name: Name of the signal
            payload: Optional data to pass to handlers
        """
        if self._enable_logging:
            logger.debug(f"[EngineSignalHub] Concurrent emitting signal '{signal_name}' with payload: {payload}")
        
        # Execute sync handlers immediately
        self.emit(signal_name, payload)
        
        # Fire async handlers in background
        async_handlers = self._async_listeners.get(signal_name, [])
        if async_handlers:
            # Create task in the event loop
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(self._execute_async_handlers(signal_name, async_handlers, payload))
            except RuntimeError:
                # No event loop running, log warning
                logger.warning(f"[EngineSignalHub] Cannot emit async handlers for '{signal_name}': no event loop running")
    
    async def _execute_async_handlers(self, signal_name: str, handlers: List[tuple], payload: Any) -> None:
        """Helper to execute async handlers with error handling."""
        async def safe_call(handler, metadata):
            try:
                await handler(payload)
            except Exception as e:
                handler_name = metadata.get("name", "unknown")
                logger.error(f"[EngineSignalHub] Error in async handler '{handler_name}' for signal '{signal_name}': {e}")
                if signal_name != "handler_error":
                    self.emit("handler_error", {
                        "signal": signal_name,
                        "handler": handler_name,
                        "error": str(e),
                        "async": True
                    })
        
        tasks = [safe_call(handler, metadata) for handler, metadata in handlers]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def registered_signals(self) -> List[str]:
        """
        Return list of all signal names that have registered handlers.
        
        Returns:
            List of signal names
        """
        sync_signals = set(self._listeners.keys())
        async_signals = set(self._async_listeners.keys())
        return sorted(sync_signals | async_signals)
    
    def get_handler_count(self, signal_name: str) -> Dict[str, int]:
        """
        Get the number of handlers registered for a signal.
        
        Args:
            signal_name: Name of the signal
            
        Returns:
            Dictionary with 'sync' and 'async' handler counts
        """
        return {
            "sync": len(self._listeners.get(signal_name, [])),
            "async": len(self._async_listeners.get(signal_name, []))
        }