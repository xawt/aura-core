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
        parts = command.strip().split(maxsplit=1)
        cmd = parts[0]
        arg = parts[1] if len(parts) > 1 else ""

        match cmd:
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
                if arg:
                    self.agent.llm.model = arg
                    updated = Text()
                    updated.append(" MATRIX UPDATED ", style=f"bold {_ORANGE}")
                    updated.append("▶ ", style=_ORANGE)
                    updated.append(self.agent.llm.model, style=_TAN)
                    console.print(updated)
                else:
                    row = Text()
                    row.append(" ACTIVE MATRIX ", style=f"bold {_BLUE}")
                    row.append("▶ ", style=_BLUE)
                    row.append(self.agent.llm.model, style=f"bold {_ORANGE}")
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

            case "/tools":
                self._handle_tools_command(arg)

            case "/exit":
                raise KeyboardInterrupt

            case _:
                row = Text()
                row.append(" UNKNOWN CMD   ", style=f"bold {_RED}")
                row.append("▶ ", style=_RED)
                row.append(command, style=_TAN)
                console.print(row)

    def _handle_tools_command(self, arg: str) -> None:
        from tools import scanner
        parts = arg.strip().split(maxsplit=1)
        sub = parts[0].lower() if parts and parts[0] else ""

        if sub in ("on", "off"):
            name = parts[1].strip() if len(parts) > 1 else ""
            if not name:
                row = Text()
                row.append(" TOOL CTRL     ", style=f"bold {_RED}")
                row.append("▶ ", style=_RED)
                row.append("Usage: /tools on|off <name>", style=_TAN)
                console.print(row)
                return
            enabled = sub == "on"
            found = scanner.set_tool_enabled(name, enabled)
            if found:
                from main import _PROJECT_ROOT
                self.agent.tool_registry = scanner.sync_and_build(
                    project_root=_PROJECT_ROOT
                )
                label = "ENABLED " if enabled else "DISABLED"
                row = Text()
                row.append(f" TOOL {label} ", style=f"bold {_ORANGE}")
                row.append("▶ ", style=_ORANGE)
                row.append(name, style=_TAN)
                console.print(row)
            else:
                row = Text()
                row.append(" TOOL CTRL     ", style=f"bold {_RED}")
                row.append("▶ ", style=_RED)
                row.append(f"Unknown tool: {name}", style=_TAN)
                console.print(row)
        else:
            # List all tools
            tools = scanner.list_tools()
            console.rule(style=_ORANGE)
            console.print(Text("  SUBROUTINES", style=f"bold {_ORANGE}"))
            if not tools:
                console.print(Text("  (none found)", style=f"dim {_TAN}"))
            for t in tools:
                tag = "[ON] " if t["enabled"] else "[OFF]"
                style = f"bold {_BLUE}" if t["enabled"] else f"bold {_RED}"
                row = Text(f"  {tag} {t['name']:<18}", style=style)
                row.append(f"  {t['module']}", style=f"dim {_TAN}")
                console.print(row)
            console.print(Text(
                "  /tools on|off <name>  to toggle",
                style=f"dim {_TAN}",
            ))
            console.rule(style=_ORANGE)

    def _print_help(self) -> None:
        from tools import scanner
        console.print()
        title = (
            f"[bold {_ORANGE}]AURA COMMAND DIRECTORY"
            f"[/bold {_ORANGE}]"
        )
        console.rule(title, style=_ORANGE)
        console.print()

        console.print(Text("  COMMANDS", style=f"bold {_ORANGE}"))
        for cmd, desc in [
            ("/help",                    "display command directory"),
            ("/model [<name>]",          "view or change active matrix"),
            ("/tools [on|off <name>]",   "list or toggle subroutines"),
            ("/reset",                   "purge memory core"),
            ("/clear",                   "clear display"),
            ("/exit",                    "terminate interface"),
        ]:
            row = Text(f"  {cmd:<28}", style=f"bold {_BLUE}")
            row.append(f"  {desc}", style=f"dim {_TAN}")
            console.print(row)

        console.print()
        console.print(Text("  SUBROUTINES", style=f"bold {_ORANGE}"))
        for t in scanner.list_tools():
            tag = "[ON] " if t["enabled"] else "[OFF]"
            style = f"bold {_BLUE}" if t["enabled"] else f"bold {_RED}"
            row = Text(f"  {tag} {t['name']:<18}", style=style)
            row.append(f"  {t['module']}", style=f"dim {_TAN}")
            console.print(row)

        console.print()
        console.rule(style=_ORANGE)
        console.print()
