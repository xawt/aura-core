import json
from pathlib import Path

from agent.context import Context
from agent.events import EventBus, FinalAnswerEvent, ToolCallEvent
from agent.llm import LLMClient
from tools.registry import ToolRegistry


class Agent:
    def __init__(self, tool_registry: ToolRegistry, project_root: Path | None = None):
        self.context = Context()
        self.bus = EventBus()
        self.llm = LLMClient()
        self.tool_registry = tool_registry
        self.project_root = project_root
        # add system prompt
        self.context.add_message(
            "system",
            "You are a helpful assistant. "
            "Use available tools whenever you need current "
            "or real-time information."
        )

    def subscribe(self, handler) -> None:
        self.bus.subscribe(handler)

    def run(self, user_input: str) -> None:
        self.context.add_message("user", user_input)
        registry = self.tool_registry  # snapshot so a concurrent /tools toggle can't race mid-run

        while True:

            message = self.llm.complete(
                self.context.get_messages(),
                tools=registry.get_all_schemas()
            )
            if message.tool_calls:
                # 1. Store the tool call message in the context
                self.context.add_tool_request(message)

                # 2. For each tool call, execute the tool and store the result
                for tool_call in message.tool_calls:
                    name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)

                    tool = registry[name]

                    self.bus.emit(ToolCallEvent(tool_name=name, args=args))
                    result = tool.fn(**args)

                    self.context.add_tool_message(
                        tool_call.id, name, str(result)
                    )
            else:
                # not a tool call, must be final answer
                self.context.add_message("assistant", message.content)
                self.bus.emit(FinalAnswerEvent(content=message.content))
                break
