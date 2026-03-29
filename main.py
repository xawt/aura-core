from agent.agent import Agent
from tools.registry import ToolRegistry, Tool
import tools.builtin.web_search
from interfaces.cli.interface import CLIInterface


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

    cli = CLIInterface(agent=agent)
    cli.run()


if __name__ == "__main__":
    main()
