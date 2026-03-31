from agent.agent import Agent
from interfaces.cli.handler import CLIHandler
import os


class CLIInterface:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.handler = CLIHandler()
        self.agent.subscribe(self.handler.handle)

    def run(self) -> None:
        print("AURA-Core ready...")

        while True:
            try:
                # Read user input
                user_input = input("\naura> ")

                # Ignore empty input
                if not user_input.strip():
                    continue

                # Handle slash commands before passing to agent
                if user_input.startswith("/"):
                    self._handle_command(user_input)
                    continue

                # Pass user input to the agent
                print("")
                self.agent.run(user_input)

            except KeyboardInterrupt:  # Handle Ctrl+C to stop the agent
                print("\nBye!")
                break

    # Handle CLI commands like /help, /reset, etc.
    def _handle_command(self, command: str) -> None:
        match command.strip():
            case "/help":
                print("""
╭─────────────────────────────────╮
│           AURA-Core             │
├─────────────────────────────────┤
│ Commands                        │
│  /help     show this message    │
│  /model    show or change model │
│  /reset    clear context        │
│  /clear    clear terminal       │
│  /exit     quit                 │
├─────────────────────────────────┤
│ Tools                           │
│  web_search   search the web    │
╰─────────────────────────────────╯
""")

            case "/reset":
                self.agent.context.clear_messages()
                print("Context cleared.")

            case "/clear":
                os.system('cls' if os.name == 'nt' else 'clear')

            case "/model":
                print(f"Current model: {self.agent.llm.model}")
                new_model = input(
                    "Enter new model (or leave blank to keep current): "
                ).strip()
                if new_model:
                    self.agent.llm.model = new_model
                    print(f"Model updated to: {self.agent.llm.model}")

            case "/exit":
                raise KeyboardInterrupt

            case _:
                print(f"Unknown command: {command}")
