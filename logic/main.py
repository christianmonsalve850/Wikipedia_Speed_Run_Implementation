from logic.graph import Node
import time
from queue import PriorityQueue
import random
from logic.heuristics import semantic_heuristic
from logic.wiki_graph import get_wiki
from logic.embedding import precompute_embeddings
from cancal_event import cancel_event

wikiObj = get_wiki()

def normalize(title):
    """
    Normalize a title for comparisons.

    @param title: Title string to normalize.
    @return str: Lowercased, stripped representation.
    """
    return title.strip().lower()

def reconstruct_path(node):
    """
    Reconstruct the path from a goal node back to the root.

    @param node: Node representing the goal.
    @return list[str]: Ordered list of page titles from start to goal.
    """
    path = []
    while node is not None:
        path.append(node.page.title)
        node = node.parent
    path.reverse()  # collected child→root, so reverse
    return path

def aStar(root, start_time, time_limit, max_depth):
    """
    Best-first search using a priority queue keyed by heuristic.

    @param root: Root Node to start search from.
    @param start_time: float timestamp when search began.
    @param time_limit: float maximum allowed time (seconds).
    @param max_depth: int maximum depth to explore.
    @return Node|None: Goal node if found; otherwise None (cancel or timeout).
    """
    frontier = PriorityQueue()
    visited = set()
    frontier_set = set()
    
    frontier.put((root.heuristic, random.random(), root))
    frontier_set.add(root.page.title)

    while not frontier.empty():
        elapsed_time = time.perf_counter() - start_time
        
        if cancel_event.is_set():
            return None

        if elapsed_time >= time_limit:
            return None 
        
        _, _, node = frontier.get()

        if node.page.title in visited or node.depth >= max_depth:
            continue

        if normalize(node.page.title) == normalize(node.end):
            return node
        else:
            for child in node.children:
                try:
                    frontier_set.add(child.page.title)
                    child.add_children(semantic_heuristic, visited, frontier_set)
                    frontier.put((child.heuristic, random.random(), child))
                except Exception as e:
                    continue

            visited.add(node.page.title)

    return None

def run(start: str, end: str, k, time_limit, max_depth):
    """
    High-level entry to run a search for a path between two pages.

    @param start: Start page title.
    @param end: End page title.
    @param k: Beam width.
    @param time_limit: Search time limit in seconds.
    @param max_depth: Maximum depth to allow.
    @return dict: Result mapping with status + timing/path on success.
    """
    start_time = time.perf_counter()

    start_page = wikiObj.page(start)
    end_page = wikiObj.page(end)

    if not start_page.exists():
        return {"status": "START_NOT_FOUND"}

    if not end_page.exists():
        return {"status": "END_NOT_FOUND"}

    precompute_embeddings([start, end])

    root = Node(start_page, 0, None, end, semantic_heuristic, k)
    root.add_children(semantic_heuristic, [], [])

    cancel_event.clear()

    node = aStar(root, start_time, time_limit, max_depth)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    
    if not node:
        return {"status": "NO_PATH_FOUND"}
    
    links = reconstruct_path(node)

    return {
        "status": "OK",
        "elapsed_time": elapsed_time,
        "n_links": len(links),
        "links": links
    }