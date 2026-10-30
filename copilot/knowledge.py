"""Stage 3 - retrieval over Cynbit's public knowledge base (TF-IDF, cosine similarity)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from .config import KB_DIR
from .schemas import Evidence


class KnowledgeBase:
    def __init__(self, docs: list[dict]):
        self.docs = docs
        corpus = [f"{d['title']} {d['title']} {d['description']} {d.get('tags', '')}" for d in docs]
        self.vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
        self.matrix = self.vec.fit_transform(corpus)
        self.by_id = {d["id"]: d for d in docs}

    @classmethod
    def load(cls, directory: Path = KB_DIR) -> "KnowledgeBase":
        docs: list[dict] = []
        for path in sorted(directory.glob("*.json")):
            docs.extend(json.loads(path.read_text(encoding="utf-8")))
        return cls(docs)

    def search(self, query: str, k: int = 3, types: set[str] | None = None) -> list[Evidence]:
        sims = linear_kernel(self.vec.transform([query]), self.matrix).ravel()
        order = np.argsort(-sims)
        out: list[Evidence] = []
        for i in order:
            d = self.docs[i]
            if sims[i] <= 0 or (types and d["type"] not in types):
                continue
            out.append(Evidence(id=d["id"], type=d["type"], title=d["title"], url=d.get("url", ""),
                                score=round(float(sims[i]), 4), snippet=d["description"][:220]))
            if len(out) == k:
                break
        return out
