"""
Scoring rules for AstroQuiz Arena.

Kept in its own module so the rules are easy to explain (and tweak) in a viva:
    points = BASE + speed bonus, multiplied by the streak multiplier.
"""

BASE_POINTS = 100          # for any correct answer
MAX_SPEED_BONUS = 50       # extra points for answering instantly
STREAK_THRESHOLD = 3       # answers in a row needed to go "on fire"
STREAK_MULTIPLIER = 1.5    # multiplier once the streak is reached

POWERUPS = {
    "black_hole": {
        "name": "Black Hole",
        "icon": "🕳️",
        "desc": "Swallows two wrong answers",
    },
    "time_warp": {
        "name": "Time Warp",
        "icon": "⏳",
        "desc": "Adds +5 seconds to your clock",
    },
    "shield": {
        "name": "Force Shield",
        "icon": "🛡️",
        "desc": "Protects your streak from one miss",
    },
}
TIME_WARP_SECONDS = 5

# (minimum accuracy %, title, emoji) — checked from the top down
RANKS = [
    (90, "Galactic Legend", "🌌"),
    (70, "Mission Commander", "🧑‍🚀"),
    (40, "Astronaut", "🚀"),
    (0, "Space Cadet", "🛰️"),
]


def answer_points(correct: bool, time_taken: float, time_limit: float, streak_after: int) -> int:
    """Points for a single answer. `streak_after` is the streak including this answer."""
    if not correct:
        return 0
    time_limit = max(time_limit, 0.1)
    speed_fraction = max(0.0, min(1.0, 1.0 - time_taken / time_limit))
    points = BASE_POINTS + MAX_SPEED_BONUS * speed_fraction
    if streak_after >= STREAK_THRESHOLD:
        points *= STREAK_MULTIPLIER
    return int(round(points))


def rank_for(accuracy_pct: float) -> dict:
    for threshold, title, emoji in RANKS:
        if accuracy_pct >= threshold:
            return {"title": title, "emoji": emoji}
    return {"title": RANKS[-1][1], "emoji": RANKS[-1][2]}
