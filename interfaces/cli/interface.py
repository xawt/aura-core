import threading
from datetime import date

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import RichLog, Static, TextArea

from rich.rule import Rule
from rich.text import Text

from agent.agent import Agent
from interfaces.cli.handler import CLIHandler

# AURA colour palette
_ORANGE = "color(214)"
_BLUE = "color(111)"
_RED = "color(167)"
_TAN = "color(223)"

_CSS = """
Screen {
    background: #0a0a0a;
}
#top {
    height: 4;
    dock: top;
}
#header {
    height: 2;
    border-bottom: solid #ffaf00;
}
#modelbar {
    height: 2;
    background: #111111;
    padding-bottom: 1;
}
#output {
    background: #0a0a0a;
    border: none;
    padding: 0 1;
    scrollbar-color: #ffaf00;
}
#input {
    dock: bottom;
    border: solid #ffaf00;
    background: #111111;
    color: #ffd7af;
    height: 3;
}
#input:focus {
    border: solid #ffaf00;
}
#input .text-area--cursor {
    background: #ffaf00;
    color: #0a0a0a;
}
"""


class AURAHeader(Static):
    def __init__(self) -> None:
        super().__init__("", id="header")

    def on_mount(self) -> None:
        self._redraw()

    def on_resize(self) -> None:
        self._redraw()

    def _redraw(self) -> None:
        sd = self._stardate()
        seg_red = "█████ "
        seg_lcli = "L-CLI "
        seg_ora = "████████████ "
        seg_title = "AURA-CORE COMPUTER INTERFACE "
        seg_blue = "████████████ "
        seg_sd = f"SD {sd} "
        fixed_len = sum(len(s) for s in [
            seg_red, seg_lcli, seg_ora,
            seg_title, seg_blue, seg_sd,
        ])
        fill = max(1, self.size.width - fixed_len) * "█"

        bar = Text()
        bar.append(seg_red, style="bold color(167)")
        bar.append(seg_lcli, style=f"bold {_ORANGE}")
        bar.append(seg_ora, style=f"bold {_ORANGE}")
        bar.append(seg_title, style=f"bold {_TAN}")
        bar.append(seg_blue, style=f"bold {_BLUE}")
        bar.append(seg_sd, style=f"bold {_BLUE}")
        bar.append(fill, style="bold color(183)")
        self.update(bar)

    @staticmethod
    def _stardate() -> str:
        d = date.today()
        yday = d.timetuple().tm_yday
        sd = (d.year - 1987) * 1000.0 + (yday / 365.25) * 1000
        return f"{sd:.1f}"


class ModelBar(Static):
    def __init__(self, model: str) -> None:
        super().__init__("", id="modelbar")
        self._model = model

    def on_mount(self) -> None:
        self._redraw()

    def on_resize(self) -> None:
        self._redraw()

    def set_model(self, model: str) -> None:
        self._model = model
        self._redraw()

    def _redraw(self) -> None:
        bar = Text()
        bar.append(" SYSTEM ONLINE ", style=f"bold {_BLUE}")
        bar.append("▶ ", style=_BLUE)
        bar.append(self._model, style=f"bold {_TAN}")
        self.update(bar)


class QueryInput(TextArea):
    def on_key(self, event) -> None:
        if event.key == "enter":
            event.prevent_default()
            event.stop()
            self.app.action_submit()
        elif event.key == "ctrl+n":
            event.prevent_default()
            event.stop()
            self.insert("\n")
            self.scroll_cursor_visible()


class CLIInterface(App):
    CSS = _CSS
    BINDINGS = []

    def __init__(self, agent: Agent) -> None:
        super().__init__()
        self.agent = agent
        self.handler = CLIHandler(self._write_from_thread)
        self.agent.subscribe(self.handler.handle)

    def compose(self) -> ComposeResult:
        with Vertical(id="top"):
            yield AURAHeader()
            yield ModelBar(self.agent.llm.model)
        yield RichLog(id="output", highlight=True, markup=False)
        yield QueryInput(id="input", tab_behavior="focus")

    def on_mount(self) -> None:
        self.query_one("#input", QueryInput).focus()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        ta = event.text_area
        lines = ta.text.count("\n") + 1
        ta.styles.height = min(max(lines + 2, 3), 9)

    def action_submit(self) -> None:
        ta = self.query_one("#input", QueryInput)
        user_input = ta.text.strip()
        ta.load_text("")
        ta.styles.height = 3

        if not user_input:
            return

        log = self.query_one("#output", RichLog)
        echo = Text()
        echo.append(" QUERY      ", style=f"bold {_ORANGE}")
        echo.append("▶ ", style=_ORANGE)
        echo.append(user_input, style=_TAN)
        log.write(echo)

        if user_input.startswith("/"):
            self._handle_command(user_input)
            return

        threading.Thread(
            target=self.agent.run,
            args=(user_input,),
            daemon=True,
        ).start()

    def _write_from_thread(self, renderable) -> None:
        log = self.query_one("#output", RichLog)
        self.call_from_thread(log.write, renderable)

    def _handle_command(self, command: str) -> None:
        log = self.query_one("#output", RichLog)
        parts = command.strip().split(maxsplit=1)
        cmd = parts[0]
        arg = parts[1] if len(parts) > 1 else ""

        match cmd:
            case "/help":
                self._print_help(log)

            case "/reset":
                self.agent.context.clear_messages()
                row = Text()
                row.append(" MEMORY CORE ", style=f"bold {_ORANGE}")
                row.append("▶ ", style=_ORANGE)
                row.append("CONTEXT PURGED", style=_TAN)
                log.write(row)

            case "/clear":
                log.clear()

            case "/model":
                if arg:
                    self.agent.llm.model = arg
                    self.query_one("#modelbar", ModelBar).set_model(arg)
                    row = Text()
                    row.append(
                        " MATRIX UPDATED ",
                        style=f"bold {_ORANGE}",
                    )
                    row.append("▶ ", style=_ORANGE)
                    row.append(self.agent.llm.model, style=_TAN)
                    log.write(row)
                else:
                    row = Text()
                    row.append(
                        " ACTIVE MATRIX  ",
                        style=f"bold {_BLUE}",
                    )
                    row.append("▶ ", style=_BLUE)
                    row.append(
                        self.agent.llm.model,
                        style=f"bold {_ORANGE}",
                    )
                    log.write(row)

            case "/tools":
                self._handle_tools_command(arg, log)

            case "/exit":
                self.exit()

            case _:
                row = Text()
                row.append(" UNKNOWN CMD   ", style=f"bold {_RED}")
                row.append("▶ ", style=_RED)
                row.append(command, style=_TAN)
                log.write(row)

    def _handle_tools_command(self, arg: str, log: RichLog) -> None:
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
                log.write(row)
                return
            enabled = sub == "on"
            found = scanner.set_tool_enabled(name, enabled, project_root=self.agent.project_root)
            if found:
                self.agent.tool_registry = scanner.sync_and_build(
                    project_root=self.agent.project_root
                )
                label = "ENABLED " if enabled else "DISABLED"
                row = Text()
                row.append(f" TOOL {label} ", style=f"bold {_ORANGE}")
                row.append("▶ ", style=_ORANGE)
                row.append(name, style=_TAN)
                log.write(row)
            else:
                row = Text()
                row.append(" TOOL CTRL     ", style=f"bold {_RED}")
                row.append("▶ ", style=_RED)
                row.append(f"Unknown tool: {name}", style=_TAN)
                log.write(row)
        else:
            # List all tools
            tools = scanner.list_tools(project_root=self.agent.project_root)
            log.write(Rule(style=_ORANGE))
            log.write(Text("  SUBROUTINES", style=f"bold {_ORANGE}"))
            if not tools:
                row = Text("  (none found)", style=f"dim {_TAN}")
                log.write(row)
            for t in tools:
                tag = "[ON] " if t["enabled"] else "[OFF]"
                style = f"bold {_BLUE}" if t["enabled"] else f"bold {_RED}"
                row = Text(f"  {tag} {t['name']:<18}", style=style)
                row.append(f"  {t['module']}", style=f"dim {_TAN}")
                log.write(row)
            log.write(Text(
                "  /tools on|off <name>  to toggle",
                style=f"dim {_TAN}",
            ))
            log.write(Rule(style=_ORANGE))

    def _print_help(self, log: RichLog) -> None:
        from tools import scanner
        log.write(Rule(style=_ORANGE))
        log.write(Text("  COMMANDS", style=f"bold {_ORANGE}"))
        for cmd, desc in [
            ("/help", "display commands  [Enter=send  Ctrl+N=newline]"),
            ("/model <name>", "view or change active matrix"),
            ("/tools [on|off <name>]", "list or toggle subroutines"),
            ("/reset", "purge memory core"),
            ("/clear", "clear display"),
            ("/exit", "terminate interface"),
        ]:
            row = Text(f"  {cmd:<26}", style=f"bold {_BLUE}")
            row.append(f"  {desc}", style=f"dim {_TAN}")
            log.write(row)
        log.write(Text(""))
        log.write(Text("  SUBROUTINES", style=f"bold {_ORANGE}"))
        for t in scanner.list_tools(project_root=self.agent.project_root):
            tag = "[ON] " if t["enabled"] else "[OFF]"
            style = f"bold {_BLUE}" if t["enabled"] else f"bold {_RED}"
            row = Text(f"  {tag} {t['name']:<18}", style=style)
            row.append(f"  {t['module']}", style=f"dim {_TAN}")
            log.write(row)
        log.write(Rule(style=_ORANGE))
