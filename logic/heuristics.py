import numpy as np
from logic.embedding import get_embedding
from logic.wiki_graph import in_popular_pages

def semantic_heuristic(title: str, end) -> float:
    """
    Compute a semantic heuristic between a candidate title and a target title.

    @param title: Candidate page title to evaluate.
    @param end: Target page title.
    @return float: Heuristic score in [0, 1] where lower is better (0 = perfect match).
    """
    word_vec = get_embedding(title)
    end_vec = get_embedding(end)

    if word_vec is None or end_vec is None:
        return 1.0

    # embeddings are stored normalized in the cache
    if in_popular_pages(title):
        return 1.0 - np.dot(word_vec, end_vec) - 0.05
    
    return 1.0 - np.dot(word_vec, end_vec)