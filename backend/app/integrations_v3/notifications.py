from dataclasses import dataclass

@dataclass(slots=True)
class Notification:
    channel: str
    destination: str
    subject: str
    body: str

class NotificationRouter:
    def __init__(self) -> None:
        self._handlers = {}

    def register(self, channel: str, handler) -> None:
        self._handlers[channel] = handler

    def send(self, notification: Notification):
        if notification.channel not in self._handlers:
            raise KeyError(notification.channel)
        return self._handlers[notification.channel](notification)
