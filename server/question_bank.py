"""
Loads the space question bank from server/data/questions/*.json and builds
a fresh, shuffled set of questions for every mission.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, List

DATA_DIR = Path(__file__).parent / "data" / "questions"
DIFFICULTIES = ["easy", "medium", "hard"]
RANDOM_CATEGORY = "random"


class QuestionBank:
    def __init__(self, data_dir: Path = DATA_DIR):
        self.categories: Dict[str, dict] = {}
        self.questions: Dict[str, List[dict]] = {}
        for path in sorted(data_dir.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            cid = data["id"]
            self.categories[cid] = {
                "id": cid,
                "title": data["title"],
                "icon": data["icon"],
                "blurb": data["blurb"],
                "order": data.get("order", 99),
            }
            qs = []
            for i, q in enumerate(data["questions"]):
                assert len(q["options"]) == 4, f"{path.name} #{i}: needs 4 options"
                assert 0 <= q["answer"] < 4, f"{path.name} #{i}: bad answer index"
                assert q["difficulty"] in DIFFICULTIES, f"{path.name} #{i}: bad difficulty"
                qs.append({**q, "category": cid, "id": f"{cid}-{i}"})
            self.questions[cid] = qs
            self.categories[cid]["count"] = len(qs)

    def category_list(self) -> List[dict]:
        cats = sorted(self.categories.values(), key=lambda c: c["order"])
        total = sum(c["count"] for c in cats)
        mixed = {
            "id": RANDOM_CATEGORY,
            "title": "Random Galaxy",
            "icon": "🌌",
            "blurb": "A bit of everything from across the universe",
            "order": 0,
            "count": total,
        }
        return [mixed] + cats

    def title_for(self, category: str) -> str:
        if category == RANDOM_CATEGORY:
            return "Random Galaxy"
        return self.categories.get(category, {}).get("title", category)

    def icon_for(self, category: str) -> str:
        if category == RANDOM_CATEGORY:
            return "🌌"
        return self.categories.get(category, {}).get("icon", "✨")

    def build_set(self, category: str, difficulty: str, n: int) -> List[dict]:
        """Pick n questions. Preferred difficulty first, then top up from the rest."""
        if category == RANDOM_CATEGORY:
            pool = [q for qs in self.questions.values() for q in qs]
        else:
            pool = list(self.questions.get(category, []))
        random.shuffle(pool)
        if difficulty in DIFFICULTIES:
            preferred = [q for q in pool if q["difficulty"] == difficulty]
            rest = [q for q in pool if q["difficulty"] != difficulty]
            pool = preferred + rest
        chosen = pool[:n]
        if difficulty not in DIFFICULTIES:  # "mixed": gentle ramp from easy to hard
            order = {d: i for i, d in enumerate(DIFFICULTIES)}
            chosen.sort(key=lambda q: order[q["difficulty"]])
        return [self._shuffled(q) for q in chosen]

    @staticmethod
    def _shuffled(q: dict) -> dict:
        """Shuffle the four options so the right answer moves around."""
        order = list(range(4))
        random.shuffle(order)
        options = [q["options"][i] for i in order]
        answer = order.index(q["answer"])
        return {**q, "options": options, "answer": answer}
