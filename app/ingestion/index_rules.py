from __future__ import annotations

import logging
import pickle
import re
from pathlib import Path

from app.config import VECTOR_DB_DIR
from app.ingestion.pdf_loader import extract_document_pages
from app.utils.company import normalize_company_name
from app.utils.paths import list_documents

logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.WARNING)


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start += chunk_size - overlap

    return chunks


def infer_company_from_document_name(file_name: str) -> str:
    lowered = file_name.lower()

    if "construtiva" in lowered:
        return "Construtiva Engenharia"
    if "vitalcare" in lowered:
        return "VitalCare"
    if "vitalis" in lowered:
        return "Rede Vitalis"
    if "logitrans" in lowered:
        return "LogiTrans Global"

    stem = Path(file_name).stem.replace("_", " ").replace("-", " ").strip()
    return normalize_company_name(stem)


def rebuild_index() -> dict:
    VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
    index_file = VECTOR_DB_DIR / "rules_index.pkl"

    documents = list_documents()

    logger.warning("Documentos encontrados: %d", len(documents))

    index_entries = []
    total_chunks = 0

    for document_path in documents:
        pages = extract_document_pages(document_path)
        company = infer_company_from_document_name(document_path.name)

        file_chunks = 0

        for page in pages:
            page_text = page.get("text", "").strip()
            page_number = page.get("page", 1)

            chunks = chunk_text(page_text)
            for chunk in chunks:
                index_entries.append(
                    {
                        "text": chunk,
                        "metadata": {
                            "source_file": document_path.name,
                            "page": page_number,
                            "company": company,
                            "doc_type": page.get("doc_type", document_path.suffix.lower().replace(".", "")),
                        },
                    }
                )

            file_chunks += len(chunks)

        total_chunks += file_chunks

        logger.warning(
            "Indexado %s | empresa=%s | chunks=%d",
            document_path.name,
            company,
            file_chunks,
        )

    payload = {
        "documents": len(documents),
        "chunks": total_chunks,
        "entries": index_entries,
    }

    with open(index_file, "wb") as f:
        pickle.dump(payload, f)

    logger.warning("Index pronto com %d chunks", total_chunks)

    return {
        "documents": len(documents),
        "chunks": total_chunks,
        "index_file": str(index_file),
    }


def load_index() -> dict:
    index_file = VECTOR_DB_DIR / "rules_index.pkl"

    if not index_file.exists():
        rebuild_index()

    with open(index_file, "rb") as f:
        payload = pickle.load(f)

    return payload