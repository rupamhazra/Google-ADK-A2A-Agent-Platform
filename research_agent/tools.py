import requests


def search_topic(query: str) -> dict:
    """Searches Wikipedia for a topic and returns a short extract."""
    response = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "generator": "search",
            "gsrsearch": query,
            "gsrlimit": 3,
            "prop": "extracts|info",
            "exintro": True,
            "explaintext": True,
            "inprop": "url",
            "format": "json",
        },
        timeout=20,
    )
    response.raise_for_status()
    pages = response.json().get("query", {}).get("pages", {})
    results = [
        {
            "title": page.get("title"),
            "extract": page.get("extract", "")[:1500],
            "url": page.get("fullurl"),
        }
        for page in pages.values()
    ]
    return {"status": "success", "query": query, "results": results}
