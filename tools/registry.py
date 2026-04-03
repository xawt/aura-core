from dataclasses import dataclass, field
from typing import Callable


# Represents a single callable tool with metadata for LLM API integration.
@dataclass
class Tool:
    name: str
    description: str
    fn: Callable
    params: dict = field(default_factory=dict)

    # Serialize to OpenAI-compatible function-calling schema.
    def to_open_ai_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.params
            }
        }


# Central registry for all tools available to the agent.
class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    # Add a tool to the registry. Raises if a tool with the same name exists.
    def register(self, tool: Tool):
        if tool.name in self._tools:
            raise ValueError(
                f"Tool with name '{tool.name}' is already registered."
            )
        self._tools[tool.name] = tool

    # Look up a tool by name. Raises KeyError if not found.
    def __getitem__(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(
                f"Tool with name '{name}' is not registered."
            )
        return self._tools[name]

    # Return OpenAI-compatible schemas for all registered tools.
    def get_all_schemas(self) -> list[dict]:
        return [tool.to_open_ai_schema() for tool in self._tools.values()]

    # Return the names of all registered tools.
    def get_all_names(self) -> list[str]:
        return list(self._tools.keys())

    # Remove all registered tools.
    def clear(self) -> None:
        self._tools.clear()
