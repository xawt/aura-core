from agent.context import Context
from agent.events import EventBus, FinalAnswerEvent
from agent.llm import LLMClient


class Agent:
    def __init__(self):
        self.context = Context()
        self.bus = EventBus()
        self.llm = LLMClient()

    def subscribe(self, handler) -> None:
        self.bus.subscribe(handler)

    def run(self, user_input: str) -> None:
        self.context.add_message("user", user_input)

        message = self.llm.complete(self.context.get_messages())

        self.context.add_message("assistant", message.content)
        self.bus.emit(FinalAnswerEvent(content=message.content))
