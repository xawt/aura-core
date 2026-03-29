from agent.agent import Agent
from agent.events import FinalAnswerEvent, ToolCallEvent
from tools.registry import ToolRegistry, Tool
import tools.builtin.web_search


def handle_answer(event):
    if isinstance(event, FinalAnswerEvent):
        print(f"{event.content}")

    if isinstance(event, ToolCallEvent):
        print(f"\n>> Tool call: {event.tool_name}\n")
        # print(f"!!! Tool call: {event.tool_name} with args {event.args}")


def main():
    tool_registry = ToolRegistry()

    # register the web search tool
    web_search_tool = Tool(
        name=tools.builtin.web_search.NAME,
        description=tools.builtin.web_search.DESCRIPTION,
        params=tools.builtin.web_search.SCHEMA,
        fn=tools.builtin.web_search.web_search
    )
    tool_registry.register(web_search_tool)

    agent = Agent(tool_registry=tool_registry)
    agent.subscribe(handle_answer)

    print("AURA-Core ready...")
    while True:
        try:
            user_input = input("aura> ")
            if not user_input.strip():
                continue
            agent.run(user_input)
        except KeyboardInterrupt:
            print("\nExiting AURA-Core...")
            break


if __name__ == "__main__":
    main()
