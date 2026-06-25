"""
ScrapeGraphAI demo — extract structured data from any URL using LLMs.
Set your LLM API key in .env before running.
"""
import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph

load_dotenv()

graph_config = {
    "llm": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "openai/gpt-4o-mini",
    },
    "verbose": True,
}


def scrape(prompt: str, url: str) -> dict:
    graph = SmartScraperGraph(
        prompt=prompt,
        source=url,
        config=graph_config,
    )
    return graph.run()


if __name__ == "__main__":
    result = scrape(
        prompt="Extract the page title and main heading.",
        url="https://example.com",
    )
    print(result)
