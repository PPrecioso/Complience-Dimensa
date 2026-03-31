from __future__ import annotations

import math
import re
from collections import Counter

from app.ingestion.index_rules import load_index
from app.utils.company import normalize_company_name


def tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s]", " ", text)
    return [token for token in text.split() if len(token) > 1]


def cosine_similarity(counter_a: Counter, counter_b: Counter) -> float:
    if not counter_a or not counter_b:
        return 0.0

    common = set(counter_a.keys()) & set(counter_b.keys())
    dot = sum(counter_a[token] * counter_b[token] for token in common)

    norm_a = math.sqrt(sum(v * v for v in counter_a.values()))
    norm_b = math.sqrt(sum(v * v for v in counter_b.values()))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


class RuleRetriever:
    def __init__(self):
        self.payload = load_index()
        self.entries = self.payload.get("entries", [])

    def search(self, company: str, sector: str, top_k: int = 5) -> list[dict]:
        company = normalize_company_name(company)
        sector = sector.strip().lower()

        query = (
            f"{company} {sector} "
            f"regras vestimenta uniforme epi equipamento proteção "
            f"capacete colete óculos luvas botas crachá apresentação pessoal"
        )
        query_counter = Counter(tokenize(query))

        scored = []

        for entry in self.entries:
            text = entry.get("text", "")
            metadata = entry.get("metadata", {})

            entry_company = normalize_company_name(metadata.get("company", ""))
            if entry_company != company:
                continue

            text_lower = text.lower()
            text_counter = Counter(tokenize(text))

            score = cosine_similarity(query_counter, text_counter)

            if sector and sector in text_lower:
                score += 0.25

            if "operacional" in text_lower:
                score += 0.08
            if "epi" in text_lower:
                score += 0.10
            if "equipamento de proteção" in text_lower:
                score += 0.10
            if "uniforme" in text_lower:
                score += 0.08
            if "vestimenta" in text_lower:
                score += 0.08
            if "capacete" in text_lower:
                score += 0.06
            if "colete" in text_lower:
                score += 0.06
            if "crachá" in text_lower:
                score += 0.04

            if score > 0:
                scored.append(
                    {
                        "text": text,
                        "metadata": metadata,
                        "score": float(score),
                    }
                )

        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]