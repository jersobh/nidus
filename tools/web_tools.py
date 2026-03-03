import requests
from duckduckgo_search import DDGS
from langchain_core.tools import tool
from typing import List

@tool
def web_search(query: str, max_results: int = 5):
    """Search the web for a given query and return results."""
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
    
    if not results:
        return "No results found."
    
    formatted_results = []
    for r in results:
        formatted_results.append(f"Title: {r['title']}\nLink: {r['href']}\nSnippet: {r['body']}\n")
    
    return "\n---\n".join(formatted_results)

@tool
def read_website(url: str):
    """Fetch the content of a website and return as text (markdown-like if possible)."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        # Simple text extraction. For better results, one could use BeautifulSoup or a dedicated library.
        return response.text[:5000] # Limit to avoid context overflow
    except Exception as e:
        return f"Error reading website {url}: {e}"

@tool
def open_documentation(tech_name: str):
    """Try to find and return documentation links for a specific technology."""
    query = f"{tech_name} official documentation"
    return web_search(query, max_results=3)
