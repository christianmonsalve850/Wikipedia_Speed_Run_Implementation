import requests
import json
from flask_app.logic.wiki_graph import get_wiki
import random

test_number = 0

HEADERS = {
    "User-Agent": "WikiSpeedRunner/1.0 (christian@example.com)"
}

def get_random_page():
    """
    Fetch a random main-namespace page title from MediaWiki.

    @return str: Random article title.
    """
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "random",
        "rnnamespace": 0,
        "rnlimit": 1
    }

    response = requests.get(url, params=params, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    title = data["query"]["random"][0]["title"]
    
    return title

def generate_random_test():
    """
    Generate a test with independently chosen start and end.

    @return dict: Test case dict ready for tests.json.
    """
    global test_number

    start = get_random_page()
    end = get_random_page()

    data_to_write = {
        "test_number": test_number,
        "start": start,
        "end": end,
        "path": "unkown",
        "category": "random",
    }

    test_number += 1

    return data_to_write

def generate_reachable_pair(start, steps=4):
    """
    Walk outgoing links from a start page to produce a reachable pair.

    @param start: Start page title.
    @param steps: Number of link-follow steps to attempt.
    @return dict: Test case where end is reachable from start and path list.
    """
    global test_number

    current = start
    path = [current]

    for _ in range(steps):
        links = list(get_wiki().page(current).links.keys())
        if not links:
            break
        current = random.choice(links)
        path.append(current)

    data_to_write = {
        "test_number": test_number,
        "start": start,
        "end": path[-1],
        "path": path,
        "category": "common"
    }

    test_number += 1

    return data_to_write


def generate_test_cases():
    """
    Generate many reachable test cases and write them to tests.json.

    @return None
    """
    popular_pages = list(get_wiki().page("Wikipedia:Popular_pages").links.keys())

    test_cases = []

    for _ in range(100):
        start = random.choice(popular_pages)
        test_cases.append(generate_reachable_pair(start, random.randint(2, 8)))

    with open("tests.json", "w", encoding="utf-8") as json_file:
        json.dump(test_cases, json_file, indent=4, ensure_ascii=False)

# generate_test_cases()  # Disabled by default.