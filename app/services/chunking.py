import re


def chunk_text(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into ~size-character chunks, cutting at sentence/space boundaries."""
    text = re.sub(r"\s+", " ", text).strip()
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            cut = max(text.rfind(". ", start, end), text.rfind(" ", start, end))
            end = cut + 1 if cut > start + size // 2 else end
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return [c for c in chunks if c]
