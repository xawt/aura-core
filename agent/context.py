class Context:
    def __init__(self):
        self._messages: list[dict] = []

    def add_tool_request(self, message) -> None:
        self._messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": message.tool_calls,
        })

    def add_tool_message(
        self, id_or_msg, name: str = None, content: str = None
    ) -> None:
        if isinstance(id_or_msg, str):
            self._messages.append({
                "role": "tool",
                "tool_call_id": id_or_msg,
                "name": name,
                "content": content,
            })
        else:
            self._messages.append(id_or_msg)

    def add_message(self, role, message) -> None:
        self._messages.append({
            "role": role,
            "content": message,
        })

    def get_messages(self) -> list[dict]:
        return self._messages

    def clear_messages(self) -> None:
        self._messages = []
