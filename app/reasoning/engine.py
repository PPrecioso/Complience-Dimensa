from __future__ import annotations
from pathlib import Path
from app.retrieval.retriever import RuleRetriever
from app.vision.detector import PersonDetector
from app.vision.cropper import crop_people
from app.vision.compliance_checker import check_basic_compliance


class ComplianceEngine:
    def __init__(self):
        self.retriever = RuleRetriever()
        self.detector = PersonDetector()

    def run(self, image_path: str, company: str, sector: str) -> dict:
        rules = self.retriever.search(company=company, sector=sector)
        detections = self.detector.detect_people(image_path)
        people = crop_people(image_path, detections)

        results = []
        status_summary = {"Conforme": 0, "Não conforme": 0, "Indeterminado": 0}

        for person in people:
            status, justificativa, required_items = check_basic_compliance(person["crop_path"], rules)
            status_summary[status] = status_summary.get(status, 0) + 1
            results.append({
                "pessoa_id": person["person_id"],
                "bbox": person["bbox"],
                "status": status,
                "justificativa": justificativa,
                "itens_requeridos": required_items,
                "crop_path": person["crop_path"],
            })

        return {
            "image_name": Path(image_path).name,
            "people_count": len(results),
            "rules_count": len(rules),
            "regras_recuperadas": rules,
            "resultado": results,
            "status_summary": status_summary,
        }
