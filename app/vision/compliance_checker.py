from __future__ import annotations


def check_basic_compliance(crop_path: str, rules: list[dict]) -> tuple[str, str, list[str]]:
    rule_text = " ".join(item["text"] for item in rules).lower()
    required_items = []
    keyword_map = {
        "capacete": "capacete",
        "colete": "colete refletivo",
        "óculos": "óculos de proteção",
        "oculos": "óculos de proteção",
        "luvas": "luvas",
        "bota": "botina de segurança",
        "botina": "botina de segurança",
        "jaleco": "jaleco",
        "máscara": "máscara",
        "mascara": "máscara",
    }
    for key, label in keyword_map.items():
        if key in rule_text and label not in required_items:
            required_items.append(label)

    if not required_items:
        return (
            "Indeterminado",
            "Não foi possível identificar requisitos claros de EPI/uniforme nas regras recuperadas para esta pessoa.",
            [],
        )

    return (
        "Indeterminado",
        "Regras relevantes recuperadas, mas a verificação visual detalhada de EPI ainda está em modo heurístico. Itens possivelmente exigidos: " + ", ".join(required_items) + ".",
        required_items,
    )
