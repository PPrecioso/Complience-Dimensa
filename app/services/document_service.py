from app.utils.paths import list_documents
from app.ingestion.pdf_loader import extract_document_pages


def get_document_catalog():
    return [
        {"name": doc.name, "path": str(doc), "type": doc.suffix.replace(".", "")}
        for doc in list_documents()
    ]


def get_document_details(doc_name: str):
    for doc in list_documents():
        if doc.name == doc_name:
            pages = extract_document_pages(doc)
            full_text = "\n".join(p["text"] for p in pages)
            return {
                "name": doc.name,
                "pages": len(pages),
                "preview": full_text[:2000],
            }
    return {"error": "document not found"}
