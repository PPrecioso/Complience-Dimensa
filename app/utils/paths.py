from pathlib import Path
from app.config import DOCS_DIR, IMAGES_DIR, VECTOR_DB_DIR, UPLOAD_DOCS_DIR, UPLOAD_IMAGES_DIR, OUTPUTS_DIR, CROPS_DIR


def ensure_directories() -> None:
    for directory in [DOCS_DIR, IMAGES_DIR, VECTOR_DB_DIR, UPLOAD_DOCS_DIR, UPLOAD_IMAGES_DIR, OUTPUTS_DIR, CROPS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def list_documents() -> list[Path]:
    ensure_directories()
    documents = []
    for folder in [DOCS_DIR, UPLOAD_DOCS_DIR]:
        if folder.exists():
            for file_path in folder.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in {".pdf", ".docx"}:
                    documents.append(file_path)
    return sorted(documents)


def list_images() -> list[Path]:
    ensure_directories()
    images = []
    for folder in [IMAGES_DIR, UPLOAD_IMAGES_DIR]:
        if folder.exists():
            for file_path in folder.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
                    images.append(file_path)
    return sorted(images)
