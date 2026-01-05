class EngineSignalHub:
    def __init__(self):
        self.listeners = {}

    def on(self, event_name, callback):
        self.listeners.setdefault(event_name, []).append(callback)

    def emit(self, event_name, data=None):
        for cb in self.listeners.get(event_name, []):
            cb(data)



#UNTESTED