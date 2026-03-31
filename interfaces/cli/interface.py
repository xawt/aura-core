import os

from rich.console import Console

from agent.agent import Agent
from interfaces.cli.handler import CLIHandler

console = Console()


class CLIInterface:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.handler = CLIHandler()
        self.agent.subscribe(self.handler.handle)

    def run(self) -> None:
        console.print()
        console.print("  [bold white]◆ AURA[/bold white][dim]-Core[/dim]")
        console.print(f"  [dim]Model: {self.agent.llm.model}[/dim]")
        console.print("  [dim]Type /help for commands[/dim]")
        console.print()

        while True:
            try:
                user_input = console.input("[bold green] >[/bold green] ")

                if not user_input.strip():
                    continue

                if user_input.startswith("/"):
                    self._handle_command(user_input)
                    continue

                console.print()
                self.agent.run(user_input)
                console.print()

            except KeyboardInterrupt:
                console.print()
                console.print("  [dim]Bye![/dim]")
                console.print()
                break

    def _handle_command(self, command: str) -> None:
        match command.strip():
            case "/help":
                self._print_help()

            case "/reset":
                self.agent.context.clear_messages()
                console.print("  [dim]Context cleared.[/dim]")

            case "/clear":
                os.system('cls' if os.name == 'nt' else 'clear')

            case "/model":
                console.print(
                    f"  Current model: [bold]{self.agent.llm.model}[/bold]"
                )
                new_model = console.input(
                    "  [dim]New model (blank to keep):[/dim] "
                ).strip()
                if new_model:
                    self.agent.llm.model = new_model
                    console.print(
                        f"  [dim]Switched to[/dim]"
                        f" [bold]{self.agent.llm.model}[/bold]"
                    )

            case "/exit":
                raise KeyboardInterrupt

            case _:
                console.print(f"  [yellow]Unknown command:[/yellow] {command}")

    def _print_help(self) -> None:
        console.print()
        console.print("  [bold]Commands[/bold]")
        for cmd, desc in [
            ("/help",  "show this message"),
            ("/model", "show or change model"),
            ("/reset", "clear context"),
            ("/clear", "clear terminal"),
            ("/exit",  "quit"),
        ]:
            console.print(
                f"  [bold cyan]{cmd:<10}[/bold cyan]  [dim]{desc}[/dim]"
            )

        console.print()
        console.print("  [bold]Tools[/bold]")
        for tool, desc in [
            ("web_search", "search the web"),
        ]:
            console.print(
                f"  [bold cyan]{tool:<12}[/bold cyan]  [dim]{desc}[/dim]"
            )
        console.print()
