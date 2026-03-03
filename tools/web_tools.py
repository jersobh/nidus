import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from langchain_core.tools import tool
from typing import List
from playwright.sync_api import sync_playwright
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
    """Fetch the content of a simple website and return as text."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        # Simple text extraction. For better results, one could use BeautifulSoup or a dedicated library.
        return response.text[:5000] # Limit to avoid context overflow
    except Exception as e:
        return f"Error reading website {url}: {e}"

@tool
def scrape_with_playwright(url: str):
    """
    Fetch the content of a website using a headless browser. 
    Use this for modern websites that require JavaScript rendering or block simple requests.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            # Wait until network is mostly idle to ensure JS has loaded
            page.goto(url, wait_until="networkidle", timeout=15000)
            
            # Simple attempt to extract text, stripping out scripts/styles
            text_content = page.evaluate('''() => {
                const scripts_and_styles = document.querySelectorAll('script, style');
                for (let el of scripts_and_styles) el.remove();
                return document.body.innerText;
            }''')
            browser.close()
            
            # Limit the output to prevent context overflow, but take more than regular read
            return text_content[:15000]
    except Exception as e:
        return f"Error reading website with playwright {url}: {e}"

@tool
def open_documentation(tech_name: str):
    """Try to find and return documentation links for a specific technology."""
    query = f"{tech_name} official documentation"
    return web_search(query, max_results=3)
