from dataclasses import dataclass, field


@dataclass
class Event:
    depth: int = 0


@dataclass
class ToolCallEvent(Event):
    tool_name: str = ""
    args: dict = field(default_factory=dict)  # each instance owns its own dict


@dataclass
class ObservationEvent(Event):
    tool_name: str = ""
    result: str = ""


@dataclass
class FinalAnswerEvent(Event):
    content: str = ""


@dataclass
class ErrorEvent(Event):
    message: str = ""


class EventBus:
    def __init__(self):
        self._handlers: list = []

    def subscribe(self, handler) -> None:
        self._handlers.append(handler)

    def emit(self, event: Event) -> None:
        for handler in self._handlers:
            handler(event)
