from pathlib import Path
import fitz
from docx import Document


def extract_pdf_pages(file_path: Path) -> list[dict]:
    pages = []
    doc = fitz.open(file_path)
    for i, page in enumerate(doc):
        text = page.get_text("text")
        if text and text.strip():
            pages.append(
                {
                    "page": i + 1,
                    "text": text,
                    "source_file": file_path.name,
                    "doc_type": "pdf",
                }
            )
    return pages


def extract_docx_pages(file_path: Path) -> list[dict]:
    doc = Document(file_path)
    text = "\n".join(p.text for p in doc.paragraphs if p.text and p.text.strip())
    return [
        {
            "page": 1,
            "text": text,
            "source_file": file_path.name,
            "doc_type": "docx",
        }
    ]


def extract_document_pages(file_path: Path) -> list[dict]:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf_pages(file_path)
    if suffix == ".docx":
        return extract_docx_pages(file_path)
    return []
