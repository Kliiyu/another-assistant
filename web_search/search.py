import requests

def search_web(query: str) -> str:
    print(f"[Web Search] Searching for: {query}")
    response = requests.get("https://api.duckduckgo.com/", params={"q": query, "format": "json"})
    if response.ok:
        data = response.json()
        return data.get("AbstractText") or "No relevant results found."
    return "Web search failed."
