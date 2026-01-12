import wikipediaapi

_wiki = None
_popular_pages_titles = None

def get_wiki():
    """
    Return a cached wikipediaapi.Wikipedia client.

    @return wikipediaapi.Wikipedia: Wikipedia client.
    """
    global _wiki
    if _wiki is None:
        _wiki = wikipediaapi.Wikipedia(
            user_agent='SpeedRun (merlin@example.com)',
            language='en'
        )
    return _wiki

def cheap_filter(link):
    """
    Lightweight filter to exclude non-article or unsuitable titles.

    @param link: wikipediaapi.WikipediaPage object.
    @return bool: True if the link should be considered for expansion.
    """
    title = link.title
    
    if ":" in title:
        return False
    if len(title) > 30:
        return False
    if sum(c.isalpha() for c in title) < 3:
        return False
    
    return True

def get_links(page: wikipediaapi.WikipediaPage):
    """
    Get filtered outgoing links for a page.

    @param page: wikipediaapi.WikipediaPage to extract links from.
    @return list[wikipediaapi.WikipediaPage]: Filtered list of links.
    """
    links_dict = page.links
    values = links_dict.values()

    links = [link for link in values if cheap_filter(link)]

    return links

def in_popular_pages(title):
    """
    Check membership in Wikipedia:Popular_pages (cached after first use).

    @param title: Title to check.
    @return bool: True if title appears in cached popular pages list.
    """
    global _popular_pages_titles
    if _popular_pages_titles is None:
        popular = get_wiki().page("Wikipedia:Popular_pages")
        _popular_pages_titles = [l.title for l in get_links(popular)]
    return title in _popular_pages_titles
