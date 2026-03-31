from __future__ import annotations
from pathlib import Path
import cv2
from app.config import CROPS_DIR


def crop_people(image_path: str, detections: list[dict]) -> list[dict]:
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

    CROPS_DIR.mkdir(parents=True, exist_ok=True)
    cropped_people = []
    stem = Path(image_path).stem

    for detection in detections:
        bbox = detection["bbox"]
        x1, y1, x2, y2 = bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"]
        crop = image[y1:y2, x1:x2]
        crop_path = CROPS_DIR / f"{stem}_person_{detection['person_id']}.png"
        cv2.imwrite(str(crop_path), crop)
        cropped_people.append({
            "person_id": detection["person_id"],
            "bbox": bbox,
            "crop_path": str(crop_path),
        })
    return cropped_people
