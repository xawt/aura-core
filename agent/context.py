class Context:
    def __init__(self):
        self._messages: list[dict] = []

    def add_tool_message(
        self, tool_call_id: str, name: str, content: str
    ) -> None:
        self._messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": name,
            "content": content,
        })

    def add_message(self, role, message) -> None:
        self._messages.append({
            "role": role,
            "content": message,
        })

    def get_messages(self) -> list[dict]:
        return self._messages

    def clear_messages(self) -> None:
        self._messages = []
