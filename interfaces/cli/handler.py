from agent.events import Event, ToolCallEvent, ObservationEvent, FinalAnswerEvent, ErrorEvent


class CLIHandler:

    # Catch all LLM events and print them to the console.
    def handle(self, event: Event) -> None:
        match event:
            case ToolCallEvent():
                print(f"🔧 {event.tool_name}({event.args})")
            case ObservationEvent():
                print(f"👁  {event.tool_name} → {event.result[:100]}...")
            case FinalAnswerEvent():
                print(f"\n{event.content}")
            case ErrorEvent():
                print(f"❌ {event.message}")