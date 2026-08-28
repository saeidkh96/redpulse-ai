from abc import ABC, abstractmethod
from collections import defaultdict

class EventBus(ABC):
    @abstractmethod
    def publish(self, topic: str, event: dict) -> None: ...
    @abstractmethod
    def subscribe(self, topic: str, handler) -> None: ...

class InMemoryEventBus(EventBus):
    def __init__(self):
        self.handlers = defaultdict(list)
        self.published = []

    def publish(self, topic, event):
        self.published.append((topic, event))
        for handler in self.handlers.get(topic, []):
            handler(event)

    def subscribe(self, topic, handler):
        self.handlers[topic].append(handler)
