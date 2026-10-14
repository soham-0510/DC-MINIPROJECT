"""
Data models that live ONLY on the server.

Clients never get these objects directly — the remote methods convert them
to plain dicts/lists before returning them over the wire (Pyro5 serializes
plain Python types).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from scoring import POWERUPS

# Game phases (a tiny state machine driven by the server clock)
LOBBY = "lobby"          # waiting for crew to join
LAUNCH = "launch"        # 3-2-1 rocket countdown before question 1
QUESTION = "question"    # a question is live
REVEAL = "reveal"        # correct answer + scores shown
FINISHED = "finished"    # podium

LAUNCH_SECONDS = 4.0
REVEAL_SECONDS = 6.0
OFFLINE_AFTER = 12.0     # seconds without a poll before a player shows as "signal lost"


@dataclass
class Player:
    id: str
    name: str
    avatar: str
    joined_at: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    score: int = 0
    streak: int = 0
    best_streak: int = 0
    correct: int = 0
    answered: int = 0
    total_time: float = 0.0
    powerups: Dict[str, bool] = field(default_factory=lambda: {k: True for k in POWERUPS})
    shield_active: bool = False
    # q_index -> {"option": int|None, "time": float, "correct": bool, "points": int}
    answers: Dict[int, dict] = field(default_factory=dict)

    @property
    def online(self) -> bool:
        return time.time() - self.last_seen < OFFLINE_AFTER

    def reset_for_new_game(self) -> None:
        self.score = self.streak = self.best_streak = self.correct = self.answered = 0
        self.total_time = 0.0
        self.powerups = {k: True for k in POWERUPS}
        self.shield_active = False
        self.answers = {}

    def public(self, host_id: str) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "avatar": self.avatar,
            "score": self.score,
            "streak": self.streak,
            "online": self.online,
            "is_host": self.id == host_id,
            "shield_active": self.shield_active,
            "joined_at": self.joined_at,
        }


@dataclass
class Room:
    code: str
    sector: str
    host_id: str
    category: str
    difficulty: str
    num_questions: int
    time_per_q: int
    players: Dict[str, Player] = field(default_factory=dict)
    questions: List[dict] = field(default_factory=list)
    phase: str = LOBBY
    q_index: int = -1
    phase_started: float = field(default_factory=time.time)
    phase_ends: Optional[float] = None
    created_at: float = field(default_factory=time.time)
    games_played: int = 0
    # per-question extras, reset every question
    warp: Dict[str, float] = field(default_factory=dict)      # player id -> extra seconds
    hidden: Dict[str, List[int]] = field(default_factory=dict)  # player id -> options removed by Black Hole
    # cumulative score after each question, for the "mission trajectory" chart
    score_history: List[Dict[str, int]] = field(default_factory=list)

    @property
    def current_question(self) -> Optional[dict]:
        if 0 <= self.q_index < len(self.questions):
            return self.questions[self.q_index]
        return None

    def settings(self) -> dict:
        return {
            "category": self.category,
            "difficulty": self.difficulty,
            "num_questions": self.num_questions,
            "time_per_q": self.time_per_q,
        }
