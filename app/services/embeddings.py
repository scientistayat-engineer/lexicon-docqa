"""all-MiniLM-L6-v2 sentence-transformer, served through ONNX (fastembed) so it
stays small enough for serverless deployment. Same model, same 384-dim vectors."""
from functools import lru_cache

from app.config import settings


@lru_cache(maxsize=1)
def _model():
    from fastembed import TextEmbedding
    return TextEmbedding(model_name=settings.embedding_model, cache_dir=settings.model_cache)


def embed(texts: list[str]) -> list[list[float]]:
    return [v.tolist() for v in _model().embed(texts)]
