from __future__ import annotations
import os
import shutil
from pathlib import Path
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.api import static
from app.config import STATIC_DIR, UPLOAD_DOCS_DIR, UPLOAD_IMAGES_DIR, IMAGES_DIR, UPLOAD_IMAGES_DIR
from app.db.database import Base, engine, get_db
from app.db.models import AnalysisRun
from app.ingestion.index_rules import rebuild_index
from app.services.analysis_service import analyze_image
from app.services.document_service import get_document_catalog, get_document_details
from app.services.storage_service import save_analysis_run, sync_assets
from app.utils.paths import ensure_directories, list_images

ensure_directories()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Compliance AI Dashboard")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/data-images", StaticFiles(directory="data/images"), name="data-images")
app.mount("/upload-images", StaticFiles(directory="uploads/images"), name="upload-images")


@app.get("/")
def home():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/assets")
def assets():
    payload = sync_assets()
    return payload


@app.get("/api/documents")
def documents():
    return get_document_catalog()


@app.get("/api/documents/{doc_name}")
def document_details(doc_name: str):
    details = get_document_details(doc_name)
    if "error" in details:
        raise HTTPException(status_code=404, detail=details["error"])
    return details


@app.get("/api/images")
def images():
    return [{"name": p.name, "path": str(p)} for p in list_images()]


@app.post("/api/upload/document")
def upload_document(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in {".pdf", ".docx"}:
        raise HTTPException(status_code=400, detail="Envie PDF ou DOCX.")
    destination = UPLOAD_DOCS_DIR / file.filename
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "Documento enviado com sucesso.", "file": file.filename}


@app.post("/api/upload/image")
def upload_image(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise HTTPException(status_code=400, detail="Envie PNG, JPG, JPEG ou WEBP.")
    destination = UPLOAD_IMAGES_DIR / file.filename
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "Imagem enviada com sucesso.", "file": file.filename}


@app.post("/api/reindex")
def reindex():
    payload = rebuild_index()
    return {"message": "Índice reconstruído com sucesso.", **payload}


@app.post("/api/analyze")
def analyze(company: str = Form(...), sector: str = Form(...), image_name: str = Form(...), db: Session = Depends(get_db)):
    image_map = {p.name: str(p) for p in list_images()}
    image_path = image_map.get(image_name)
    if not image_path:
        raise HTTPException(status_code=404, detail="Imagem não encontrada.")

    result, result_path = analyze_image(image_path=image_path, company=company, sector=sector)
    save_analysis_run(db, result=result, company=company, sector=sector, image_path=image_path, result_path=result_path)
    return result


@app.get("/api/history")
def history(db: Session = Depends(get_db)):
    rows = db.query(AnalysisRun).order_by(AnalysisRun.id.desc()).limit(20).all()
    return [
        {
            "id": row.id,
            "company": row.company,
            "sector": row.sector,
            "image_name": row.image_name,
            "people_count": row.people_count,
            "rules_count": row.rules_count,
            "status_summary": row.status_summary,
            "result_path": row.result_path,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
        for row in rows
    ]
