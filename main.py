from agent.agent import Agent
from agent.events import FinalAnswerEvent

def handle_answer(event: FinalAnswerEvent):
    if isinstance(event, FinalAnswerEvent):
        print(f"{event.content}")

def main():
    
    agent = Agent()
    agent.subscribe(handle_answer)

    print("AURA-Core ready...")
    try:                
        q = input("aura> ") 
        agent.run(q)
    except KeyboardInterrupt:
        print("\nExiting AURA-Core...")

if __name__ == "__main__":
    main()