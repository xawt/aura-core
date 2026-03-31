import os
from openai import OpenAI
from dotenv import load_dotenv
from agent.config import load_config

load_dotenv()

DEFAULT_MODEL = "google/gemini-2.0-flash-001"


class LLMClient:
    def __init__(self, model: str | None = None):
        config = load_config('config/default.yaml')
        print(f"Config loaded: {config}")
        self.model = model or config.get("model", DEFAULT_MODEL)
        print(f"Using LLM model: {self.model}")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"],
        )

    def complete(
        self, messages: list[dict], tools: list[dict] | None = None
    ) -> dict:

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools
        )
        return response.choices[0].message
