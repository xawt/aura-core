# Web search tool using DuckDuckGo (via the ddgs library).
# Exposes a single function `web_search` that returns formatted results
# as a plain string, suitable for passing back to an LLM as tool output.
from datetime import date
from ddgs import DDGS


# --- Tool metadata (read by the tool loader) ---

NAME = "web_search"
DESCRIPTION = (
    "Search the web for current information. "
    "Use when you need up-to-date data, news, or facts you don't know."
)

# JSON Schema describing the expected input arguments.
SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Search query"}
    },
    "required": ["query"]
}


def web_search(query: str) -> str:
    # Query DuckDuckGo and collect up to 5 results.
    try:
        date_string = date.today().strftime("%Y-%m-%d")
        query = query + f" as of {date_string}"
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
    except Exception as e:
        # Surface network / rate-limit errors as a readable string.
        return f"Search failed: {e}"

    if not results:
        return "No results found."

    # Format each result as a short block of text.
    # Use .get() to handle incomplete records gracefully.
    output = []
    for r in results:
        output.append(
            f"Title: {r.get('title', '')}\n"
            f"URL: {r.get('href', '')}\n"
            f"Summary: {r.get('body', '')}\n"
        )

    return "\n".join(output)


# Debug main to test the tool independently.
if __name__ == "__main__":
    query = input("Search: ")
    print(web_search(query))
