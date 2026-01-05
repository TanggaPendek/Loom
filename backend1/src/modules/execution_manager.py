# modules/execution_manager.py

class ExecutionManager:

    def __init__(self, engine, signalhub):
        self.engine = engine
        self.signalhub = signalhub

        self.running = False
        self.current_run_id = None  # Optional tracking if multiple runs are queued

        # Register signal listeners
        signalhub.on("engine_run", self.run)
        signalhub.on("engine_stop", self.stop)
        signalhub.on("engine_force_stop", self.force_stop)



    def run(self, payload):
        if self.running:
            print("Execution already running")
            return

        self.running = True
        self.current_run_id = payload.get("run_id", None)

        try:
            # Call engine.run and pass callback for engine events
            self.engine.run(payload, callback=self._engine_callback)
        except Exception as e:
            self.signalhub.emit("engine_error", e)
        finally:
            self.running = False
            self.current_run_id = None

    def stop(self, payload=None):
        if self.running:
            self.engine.stop()
            self.running = False

    def force_stop(self, payload=None):
        if self.running:
            self.engine.force_stop()
            self.running = False

    # ---------- Internal engine callback ----------

    def _engine_callback(self, event_type, data):

        if event_type == "node_started":
            self.signalhub.emit("engine_node_started", data)
        elif event_type == "node_finished":
            self.signalhub.emit("engine_node_finished", data)
        elif event_type == "progress":
            self.signalhub.emit("engine_progress", data)
        elif event_type == "error":
            self.signalhub.emit("engine_error", data)




#UNTESTED