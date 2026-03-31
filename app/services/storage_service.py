from __future__ import annotations
import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.models import AnalysisRun
from app.utils.paths import list_documents, list_images


def sync_assets() -> dict:
    return {
        "documents": [p.name for p in list_documents()],
        "images": [p.name for p in list_images()],
    }


def save_analysis_run(db: Session, result: dict, company: str, sector: str, image_path: str, result_path: str) -> AnalysisRun:
    run = AnalysisRun(
        company=company,
        sector=sector,
        image_name=Path(image_path).name,
        image_path=str(image_path),
        people_count=result.get("people_count", 0),
        rules_count=result.get("rules_count", 0),
        status_summary=json.dumps(result.get("status_summary", {}), ensure_ascii=False),
        result_path=result_path,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run
