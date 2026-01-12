import requests

HEADERS = {
    "User-Agent": "WikiSpeedRunner/1.0 (christian@example.com)"
}

def wikipedia_autocomplete(query, k=5):
    """
    Query MediaWiki's opensearch endpoint for suggestions.

    @param query: Partial query string.
    @param k: Maximum suggestions to return.
    @return list[str]: Suggested page titles.
    """
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "opensearch",
        "search": query,
        "limit": k,
        "namespace": 0,
        "format": "json"
    }

    response = requests.get(url, params=params, headers=HEADERS).json()
    return response[1]