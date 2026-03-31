from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "docs"
IMAGES_DIR = DATA_DIR / "images"
VECTOR_DB_DIR = DATA_DIR / "vector_db"
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOAD_DOCS_DIR = UPLOADS_DIR / "docs"
UPLOAD_IMAGES_DIR = UPLOADS_DIR / "images"
OUTPUTS_DIR = BASE_DIR / "outputs"
CROPS_DIR = OUTPUTS_DIR / "crops"
STATIC_DIR = BASE_DIR / "app" / "api" / "static"
INDEX_FILE = VECTOR_DB_DIR / "rules_index.pkl"
YOLO_MODEL = "yolov8n.pt"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{(BASE_DIR / 'compliance_ai.db').as_posix()}")
TOP_K = 5
