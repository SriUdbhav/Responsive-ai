from pathlib import Path
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_core.tools import tool
from tavily import TavilyClient

# Load .env from the module's directory
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

_tavily_key = os.getenv("TAVILY_API_KEY")
tavily = TavilyClient(api_key=_tavily_key) if _tavily_key else None


@tool
def get_websearch(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Return Titles, URLs and snippets."""
    if not tavily:
        return "Error: TAVILY_API_KEY is not configured in .env"
    try:
        results = tavily.search(query=query, max_results=5)
        out = []
        for r in results.get("results", []):
            out.append(f'Title: {r.get("title", "No Title")}, URL: {r.get("url", "")}\nSnippet: {r.get("content", "")[:180]}')
        return "\n----\n".join(out)
    except Exception as e:
        return f"Error executing web search: {str(e)}"


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper analysis."""
    if not url or not isinstance(url, str):
        return "Error: A valid URL string must be provided."
    clean_url = url.strip().strip("'\"<>")
    if not clean_url.startswith(("http://", "https://")):
        clean_url = "https://" + clean_url

    try:
        resp = requests.get(clean_url, timeout=10, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
        for tag in soup(["script", "style", "footer", "nav", "header", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        return text[:2000] if text else "No readable text content extracted from page."
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"
