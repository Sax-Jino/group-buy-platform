class EventEmitter:
    def __init__(self):
        self.listeners = {}

    def init_app(self, app):
        self.app = app

    def on(self, event_name, handler):
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(handler)

    def emit(self, event_name, *args, **kwargs):
        if event_name in self.listeners:
            for handler in self.listeners[event_name]:
                handler(*args, **kwargs)