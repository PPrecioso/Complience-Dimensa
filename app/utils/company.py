from pathlib import Path

COMPANY_MAP = {
    "construtiva": "Construtiva Engenharia",
    "logitrans": "LogiTrans Global",
    "vitalcare": "VitalCare",
    "vitalis": "Rede Vitalis",
}


def normalize_company_name(name: str) -> str:
    raw = (name or "").strip()
    lower = raw.lower()
    for key, value in COMPANY_MAP.items():
        if key in lower:
            return value
    return raw or "Desconhecida"


def infer_company_from_filename(path: str | Path) -> str:
    name = Path(path).name.lower()
    if "construtiva" in name:
        return "Construtiva Engenharia"
    if "vitalcare" in name:
        return "VitalCare"
    if "logitrans" in name:
        return "LogiTrans Global"
    if "rede" in name or "vitalis" in name:
        return "Rede Vitalis"
    return "Desconhecida"
