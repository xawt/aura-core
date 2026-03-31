from rich.console import Console
from rich.markdown import Markdown

from agent.events import (
    Event, ToolCallEvent, ObservationEvent, FinalAnswerEvent, ErrorEvent
)

console = Console()


class CLIHandler:

    def handle(self, event: Event) -> None:
        match event:
            case ToolCallEvent():
                args_str = ", ".join(
                    f'{k}="{v}"' for k, v in event.args.items()
                )
                console.print(
                    f"  [dim]⏺ {event.tool_name}({args_str})[/dim]"
                )
            case ObservationEvent():
                raw = event.result
                preview = raw[:200] + "…" if len(raw) > 200 else raw
                console.print(f"  [dim]  ↳ {preview}[/dim]")
            case FinalAnswerEvent():
                console.print()
                console.print(Markdown(event.content))
            case ErrorEvent():
                console.print(
                    f"\n  [bold red]✗[/bold red] [red]{event.message}[/red]"
                )
