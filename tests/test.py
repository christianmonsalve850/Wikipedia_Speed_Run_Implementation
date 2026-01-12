import wikipediaapi
import requests

HEADERS = {
    "User-Agent": "WikiSpeedRunner/1.0 (christian@example.com)"
}

wik = wikipediaapi.Wikipedia(
            user_agent='SpeedRun (merlin@example.com)',
            language='en'
        )

page = wik.page("alsdkjf")

start = "barack obama"
end = "Llama"

start_page = wik.page(start)
end_page = wik.page(end)

def wikipedia_autocomplete(query, k=5):
    """
    Helper to query MediaWiki opensearch for tests.

    @param query: Partial query string.
    @param k: Number of suggestions to return.
    @return list: Suggested page titles.
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
    return response[1]  # list of suggested titles

def normalize(title):
    """
    Normalize test strings for comparison.

    @param title: Title to normalize.
    @return str: Normalized (stripped, lowercased) title.
    """
    return title.strip().lower()

def resolve_page(title: str):
    """
    Resolve a title to a wikipediaapi.WikipediaPage, attempting a search if needed.

    @param title: Title or partial title to resolve.
    @return wikipediaapi.WikipediaPage|None: Resolved page or None.
    """
    page = wik.page(title)

    if not page.exists():
        results = wik.search(title, results=1)
        if not results:
            return None
        page = wik.page(results[0])

    return page

print(resolve_page(start_page.title))