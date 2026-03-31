from __future__ import annotations
from ultralytics import YOLO
from app.config import YOLO_MODEL


class PersonDetector:
    def __init__(self):
        self.model = YOLO(YOLO_MODEL)

    def detect_people(self, image_path: str) -> list[dict]:
        results = self.model(image_path, verbose=False)
        detections = []
        person_id = 1
        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0].item())
                if cls == 0:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    detections.append({
                        "person_id": person_id,
                        "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                    })
                    person_id += 1
        return detections
