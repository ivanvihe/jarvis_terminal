import threading
import time

class EventListener:
    def __init__(self, name):
        self.name = name
        self.running = False
        self.thread = None

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False

    def run(self):
        """Este método debe ser implementado por cada listener"""
        raise NotImplementedError

class EventManager:
    def __init__(self):
        self.listeners = []

    def register_listener(self, listener: EventListener):
        self.listeners.append(listener)
        listener.start()

    def stop_all(self):
        for listener in self.listeners:
            listener.stop()
