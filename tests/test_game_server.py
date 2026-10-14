"""
Tests for the game logic. They call the remote object's methods directly
(no network), so they run in a second:

    python -m pytest tests -q        or        python tests/test_game_server.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))

import models  # noqa: E402
from game_server import AstroQuizServer  # noqa: E402
from question_bank import QuestionBank  # noqa: E402
from scoring import answer_points, rank_for  # noqa: E402


def fast_forward(server, code, seconds):
    """Pretend time has passed by shifting the room's clock backwards."""
    room = server._rooms[code]
    room.phase_started -= seconds
    if room.phase_ends:
        room.phase_ends -= seconds


def new_game(n=3, players=2):
    s = AstroQuizServer()
    r = s.create_room("Host", "🚀", "solar_system", "mixed", n, 10)
    code, host = r["code"], r["player_id"]
    ids = [host]
    for i in range(players - 1):
        ids.append(s.join_room(code, f"P{i}", "👽")["player_id"])
    assert s.start_game(code, host)["ok"]
    fast_forward(s, code, models.LAUNCH_SECONDS + 0.1)
    st = s.get_room_state(code, host)["state"]
    assert st["phase"] == "question"
    return s, code, ids


def test_question_bank_is_valid():
    bank = QuestionBank()
    assert sum(len(q) for q in bank.questions.values()) >= 100
    for qs in bank.questions.values():
        for q in qs:
            assert len(set(q["options"])) == 4, q["question"]


def test_answer_is_hidden_until_reveal():
    s, code, ids = new_game()
    st = s.get_room_state(code, ids[0])["state"]
    assert "answer" not in str(st["question"].keys())
    assert "reveal" not in st


def test_everyone_answers_triggers_reveal_and_scoring():
    s, code, ids = new_game()
    q = s._rooms[code].current_question
    s.submit_answer(code, ids[0], 0, q["answer"])
    s.submit_answer(code, ids[1], 0, (q["answer"] + 1) % 4)
    st = s.get_room_state(code, ids[0])["state"]
    assert st["phase"] == "reveal"
    res = {r["id"]: r for r in st["reveal"]["results"]}
    assert res[ids[0]]["correct"] and res[ids[0]]["points"] >= 100
    assert not res[ids[1]]["correct"] and res[ids[1]]["points"] == 0


def test_double_answer_rejected():
    s, code, ids = new_game(players=3)
    assert s.submit_answer(code, ids[0], 0, 1)["ok"]
    assert not s.submit_answer(code, ids[0], 0, 2)["ok"]


def test_timeout_moves_on_and_game_finishes():
    s, code, ids = new_game(n=3)
    for _ in range(3):
        fast_forward(s, code, 11)          # question clock runs out
        s.get_room_state(code, ids[0])
        s.get_room_state(code, ids[1])
        fast_forward(s, code, models.REVEAL_SECONDS + 0.1)
        st = s.get_room_state(code, ids[0])["state"]
    assert st["phase"] == "finished"
    assert len(st["final"]) == 2 and st["final"][0]["place"] == 1


def test_black_hole_hides_two_wrong_options():
    s, code, ids = new_game()
    r = s.use_powerup(code, ids[0], "black_hole")
    q = s._rooms[code].current_question
    assert r["ok"] and len(r["hidden"]) == 2 and q["answer"] not in r["hidden"]
    assert not s.use_powerup(code, ids[0], "black_hole")["ok"]  # once per mission


def test_only_host_can_start():
    s = AstroQuizServer()
    r = s.create_room("Host", "🚀", "random", "mixed", 3, 10)
    guest = s.join_room(r["code"], "G", "👽")["player_id"]
    assert not s.start_game(r["code"], guest)["ok"]


def test_scoring_rules():
    assert answer_points(False, 1, 10, 1) == 0
    assert answer_points(True, 0, 10, 1) == 150
    assert answer_points(True, 10, 10, 1) == 100
    assert answer_points(True, 0, 10, 3) == 225  # streak multiplier
    assert rank_for(95)["title"] == "Galactic Legend"
    assert rank_for(10)["title"] == "Space Cadet"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("✓", name)
    print("All tests passed.")
