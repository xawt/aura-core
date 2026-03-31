import argparse

from agent.agent import Agent
from tools.registry import ToolRegistry, Tool
import tools.builtin.web_search


def build_agent() -> Agent:
    tool_registry = ToolRegistry()
    web_search_tool = Tool(
        name=tools.builtin.web_search.NAME,
        description=tools.builtin.web_search.DESCRIPTION,
        params=tools.builtin.web_search.SCHEMA,
        fn=tools.builtin.web_search.web_search
    )
    tool_registry.register(web_search_tool)
    return Agent(tool_registry=tool_registry)


def main():
    parser = argparse.ArgumentParser(prog="aura")
    parser.add_argument(
        "--ui",
        choices=["tui", "rich"],
        default="tui",
        help="Interface style: tui (L-CLI, default) or rich (plain Rich)",
    )
    args = parser.parse_args()

    agent = build_agent()

    if args.ui == "rich":
        from interfaces.cli.rich_interface import RichCLIInterface
        RichCLIInterface(agent=agent).run()
    else:
        from interfaces.cli.interface import CLIInterface
        CLIInterface(agent=agent).run()


if __name__ == "__main__":
    main()
