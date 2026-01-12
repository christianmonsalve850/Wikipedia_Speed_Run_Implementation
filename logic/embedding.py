from sentence_transformers import SentenceTransformer

# Load the small ModernBERT-based model (47M parameters)
model = SentenceTransformer('ibm-granite/granite-embedding-small-english-r2')

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

    # model.encode(..., normalize_embeddings=True) returns normalized vectors
    vectors = model.encode(
        missing,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    for title, vec in zip(missing, vectors):
        embedding_cache[title] = vec