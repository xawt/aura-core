import os
from datetime import date

from rich.console import Console
from rich.text import Text

from agent.agent import Agent
from interfaces.cli.rich_handler import RichCLIHandler

# AURA colour palette
_ORANGE = "color(214)"
_BLUE = "color(111)"
_RED = "color(167)"
_PURPLE = "color(183)"
_TAN = "color(223)"

console = Console()


class RichCLIInterface:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.handler = RichCLIHandler()
        self.agent.subscribe(self.handler.handle)

    def run(self) -> None:
        self._print_header()

        while True:
            try:
                console.print()
                user_input = console.input(
                    f"[bold {_ORANGE}] QUERY ▶ [/bold {_ORANGE}] "
                )

                if not user_input.strip():
                    continue

                if user_input.startswith("/"):
                    self._handle_command(user_input)
                    continue

                console.print()
                self.agent.run(user_input)

            except KeyboardInterrupt:
                console.print()
                console.rule(
                    f"[bold {_ORANGE}]AURA INTERFACE TERMINATED"
                    f"[/bold {_ORANGE}]",
                    style=_ORANGE,
                )
                console.print()
                break

    def _print_header(self) -> None:
        console.print()
        bar = Text()
        bar.append("█████ ", style=f"bold {_RED}")
        bar.append("L-CLI ", style=f"bold {_ORANGE}")
        bar.append("████████████ ", style=f"bold {_ORANGE}")
        bar.append(
            "AURA-CORE COMPUTER INTERFACE ",
            style=f"bold {_TAN}",
        )
        bar.append("████████████ ", style=f"bold {_BLUE}")
        bar.append(f"SD {self._stardate()} ", style=f"bold {_BLUE}")
        bar.append("█████", style=f"bold {_PURPLE}")
        console.print(bar)
        console.rule(style=_ORANGE)

        sub = Text()
        sub.append("  SYSTEM ONLINE ", style=_ORANGE)
        sub.append("▶ ", style=f"dim {_ORANGE}")
        sub.append(
            f"MODEL: {self.agent.llm.model}  ",
            style=f"dim {_TAN}",
        )
        sub.append("▶ ", style=f"dim {_ORANGE}")
        sub.append("TYPE /HELP FOR COMMANDS", style=f"dim {_TAN}")
        console.print(sub)
        console.rule(style=_ORANGE)
        console.print()

    @staticmethod
    def _stardate() -> str:
        d = date.today()
        yday = d.timetuple().tm_yday
        sd = (d.year - 1987) * 1000.0 + (yday / 365.25) * 1000
        return f"{sd:.1f}"

    def _handle_command(self, command: str) -> None:
        match command.strip():
            case "/help":
                self._print_help()

            case "/reset":
                self.agent.context.clear_messages()
                row = Text()
                row.append(" MEMORY CORE ", style=f"bold {_ORANGE}")
                row.append("▶ ", style=_ORANGE)
                row.append("CONTEXT PURGED", style=_TAN)
                console.print(row)

            case "/clear":
                os.system('cls' if os.name == 'nt' else 'clear')

            case "/model":
                row = Text()
                row.append(" ACTIVE MATRIX ", style=f"bold {_BLUE}")
                row.append("▶ ", style=_BLUE)
                row.append(
                    self.agent.llm.model,
                    style=f"bold {_ORANGE}",
                )
                console.print(row)
                new_model = console.input(
                    f"[{_BLUE}] NEW MATRIX ID ▶[/{_BLUE}]  "
                ).strip()
                if new_model:
                    self.agent.llm.model = new_model
                    updated = Text()
                    updated.append(
                        " MATRIX UPDATED ",
                        style=f"bold {_ORANGE}",
                    )
                    updated.append("▶ ", style=_ORANGE)
                    updated.append(self.agent.llm.model, style=_TAN)
                    console.print(updated)

            case "/exit":
                raise KeyboardInterrupt

            case _:
                row = Text()
                row.append(" UNKNOWN CMD   ", style=f"bold {_RED}")
                row.append("▶ ", style=_RED)
                row.append(command, style=_TAN)
                console.print(row)

    def _print_help(self) -> None:
        console.print()
        title = (
            f"[bold {_ORANGE}]AURA COMMAND DIRECTORY"
            f"[/bold {_ORANGE}]"
        )
        console.rule(title, style=_ORANGE)
        console.print()

        console.print(Text("  COMMANDS", style=f"bold {_ORANGE}"))
        for cmd, desc in [
            ("/help",  "display command directory"),
            ("/model", "view or change active matrix"),
            ("/reset", "purge memory core"),
            ("/clear", "clear display"),
            ("/exit",  "terminate interface"),
        ]:
            row = Text(f"  {cmd:<12}", style=f"bold {_BLUE}")
            row.append(f"  {desc}", style=f"dim {_TAN}")
            console.print(row)

        console.print()
        console.print(Text("  SUBROUTINES", style=f"bold {_ORANGE}"))
        for tool, desc in [
            ("web_search", "query the federation database network"),
        ]:
            row = Text(f"  {tool:<14}", style=f"bold {_BLUE}")
            row.append(f"  {desc}", style=f"dim {_TAN}")
            console.print(row)

        console.print()
        console.rule(style=_ORANGE)
        console.print()
