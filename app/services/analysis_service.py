from __future__ import annotations
import json
from pathlib import Path
from app.config import OUTPUTS_DIR


def analyze_image(image_path: str, company: str, sector: str) -> tuple[dict, str]:
    from app.reasoning.engine import ComplianceEngine

    engine = ComplianceEngine()
    result = engine.run(image_path=image_path, company=company, sector=sector)

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUTS_DIR / f"{Path(image_path).stem}_result.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result, str(output_file)
