import numpy as np
from wiki_graph import get_links
from embedding import precompute_embeddings

class Node:
    """
    Node in the search tree representing a Wikipedia page.

    @param page: wikipediaapi.WikipediaPage corresponding to this node.
    @param depth: int depth in the tree (root==0).
    @param parent: Node|None parent node.
    @param end: str target page title.
    @param heuristic_fn: callable(title, end) -> float scoring function.
    @param k: int beam width (max children to keep).
    """
    def __init__(self, page, depth, parent, end, heuristic_fn, k):
        self.page = page
        self.depth = depth
        self.children = []
        self.parent = parent
        self.end = end
        self.heuristic = heuristic_fn(page.title, end)
        self.k = k

    def beam_width(self):
        """
        Return beam width based on depth.

        @return int: beam width.
        """
        if self.depth < 3: return 5
        if self.depth < 8: return 3
        return 1
        
    def add_children(self, heuristic_fn, visited, frontier_set):
        """
        Expand outgoing links into child Nodes and keep top-k by heuristic.

        @param heuristic_fn: scoring function for children.
        @param visited: set of titles already visited.
        @param frontier_set: set of titles currently in the frontier.
        @return None
        """
        links = get_links(self.page)

        if not links:
            return
        
        links = [l for l in links if (l.title not in visited) and (l.title not in frontier_set)]

        titles = [l.title for l in links]
        precompute_embeddings(titles)  # batch-encode missing titles to fill embedding cache

        children = []
        scores = []

        for link in links:
            child = Node(link, self.depth+1, self, self.end, heuristic_fn, self.k)
            children.append(child)
            scores.append(child.heuristic)

        k = min(self.k, len(scores))
        # keep top-k by heuristic using argpartition
        idx = np.argpartition(scores, k - 1)[:k]

        self.children = [children[i] for i in idx]