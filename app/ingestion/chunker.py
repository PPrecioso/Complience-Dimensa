def chunk_text(text: str, chunk_size: int = 700, overlap: int = 120) -> list[str]:
    normalized = " ".join(text.split())
    chunks = []
    start = 0
    while start < len(normalized):
        end = start + chunk_size
        chunk = normalized[start:end]
        if chunk:
            chunks.append(chunk)
        start += max(1, chunk_size - overlap)
    return chunks
