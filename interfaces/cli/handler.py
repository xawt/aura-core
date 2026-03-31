from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from agent.events import (
    Event, ToolCallEvent, ObservationEvent, FinalAnswerEvent, ErrorEvent
)

# LCARS colour palette
_ORANGE = "color(214)"
_BLUE = "color(111)"
_RED = "color(167)"
_TAN = "color(223)"

console = Console()


class CLIHandler:

    def handle(self, event: Event) -> None:
        match event:
            case ToolCallEvent():
                args_str = ", ".join(
                    f'{k}="{v}"' for k, v in event.args.items()
                )
                row = Text()
                row.append(" ACCESSING  ", style=f"bold {_ORANGE}")
                row.append("▶ ", style=_ORANGE)
                row.append(
                    f"{event.tool_name}({args_str})",
                    style=f"dim {_TAN}"
                )
                console.print(row)

            case ObservationEvent():
                raw = event.result
                preview = raw[:200] + "…" if len(raw) > 200 else raw
                row = Text()
                row.append(" DATA RECV  ", style=f"bold {_BLUE}")
                row.append("▶ ", style=_BLUE)
                row.append(preview, style=f"dim {_TAN}")
                console.print(row)

            case FinalAnswerEvent():
                title = (
                    f"[bold {_TAN}]LCARS RESPONSE[/bold {_TAN}]"
                )
                console.print()
                console.print(Panel(
                    Markdown(event.content),
                    border_style=_ORANGE,
                    title=title,
                    title_align="left",
                    padding=(1, 2),
                ))

            case ErrorEvent():
                row = Text()
                row.append(" ⚠  ALERT   ", style=f"bold {_RED}")
                row.append("▶ ", style=_RED)
                row.append(event.message, style=f"bold {_RED}")
                console.print()
                console.print(row)
