from sentence_transformers import SentenceTransformer

# Lazily create the model to avoid initializing heavy backends (e.g., MPS) at import time.
_model = None

def _get_model():
    """Return the cached SentenceTransformer model, loading it on first use."""
    global _model
    if _model is None:
        _model = SentenceTransformer('ibm-granite/granite-embedding-small-english-r2')
    return _model

embedding_cache = {}

def get_embedding(title):
    """
    Retrieve an embedding from the cache.

    @param title: Page/title to look up in the embedding cache.
    @return np.ndarray|None: Normalized vector if cached, otherwise None.
    """
    return embedding_cache.get(title)

def precompute_embeddings(titles, batch_size=64):
    """
    Encode and cache embeddings for missing titles.

    @param titles: List[str] titles to encode.
    @param batch_size: int batch size for the encoder.
    @return None
    """
    missing = [t for t in titles if t not in embedding_cache]

    if not missing:
        return

    model = _get_model()
    
    # model.encode(..., normalize_embeddings=True) returns normalized vectors
    vectors = model.encode(
        missing,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    for title, vec in zip(missing, vectors):
        embedding_cache[title] = vec