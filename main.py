import argparse
from pathlib import Path

from agent.agent import Agent
from tools.scanner import sync_and_build

_PROJECT_ROOT = Path(__file__).parent


def build_agent() -> Agent:
    registry = sync_and_build(project_root=_PROJECT_ROOT)
    return Agent(tool_registry=registry)


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
