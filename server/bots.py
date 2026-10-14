"""
Practice bots — fill a mission with AI crewmates so you can demo the
multiplayer game on one laptop.

Each bot is its own RPC client: it joins the room with join_room(), polls
get_room_state() and calls submit_answer() — exactly like a real player.

    python server/bots.py ABC123              # 3 bots join mission ABC123
    python server/bots.py ABC123 --count 5 --host 192.168.1.20

Bots guess randomly — the server never reveals the answer before everyone
has answered, so they can't cheat (and neither can a modified client).
"""

from __future__ import annotations

import argparse
import sys
import random
import threading
import time

import Pyro5.api
import Pyro5.errors

NAMES = ["HAL-9000", "Wall-E", "TARS", "R2-D2", "Baymax", "Vyommitra", "Curio", "Sputnik", "Pixel", "Orbit"]
AVATARS = ["🤖", "🛸", "👽", "🛰️", "☄️", "🌟", "🪐", "🌙"]


def run_bot(uri: str, code: str, name: str, avatar: str, stop: threading.Event) -> None:
    proxy = Pyro5.api.Proxy(uri)
    res = proxy.join_room(code, name, avatar)
    if not res.get("ok"):
        print(f"  ✗ {name}: {res['error']}")
        return
    pid = res["player_id"]
    print(f"  ✓ {res.get('name', name)} {avatar} joined mission {code}")
    answered = set()
    while not stop.is_set():
        try:
            state = proxy.get_room_state(code, pid)
        except Pyro5.errors.CommunicationError:
            time.sleep(1)
            continue
        if not state.get("ok"):
            print(f"  · {name}: {state['error']}")
            return
        s = state["state"]
        key = (s["games_played"], s["q_index"])
        if s["phase"] == "question" and key not in answered and s.get("my_answer") is None:
            # think for a human-like moment, then answer
            think = random.uniform(1.5, max(2.0, min(s["time_left"] - 0.5, 9)))
            time.sleep(think)
            choice = random.randrange(4)
            hidden = s.get("hidden", [])
            while choice in hidden:
                choice = random.randrange(4)
            proxy.submit_answer(code, pid, s["q_index"], choice)
            answered.add(key)
        time.sleep(0.8)
    try:
        proxy.leave_room(code, pid)
    except Exception:
        pass


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")  # emoji-safe on any Windows console
    ap = argparse.ArgumentParser(description="Add practice bots to an AstroQuiz mission")
    ap.add_argument("code", help="6-character mission code")
    ap.add_argument("--count", type=int, default=3)
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=9100)
    args = ap.parse_args()
    uri = f"PYRO:astroquiz.server@{args.host}:{args.port}"
    stop = threading.Event()
    names = random.sample(NAMES, k=min(args.count, len(NAMES)))
    threads = [
        threading.Thread(target=run_bot, args=(uri, args.code.upper(), n, random.choice(AVATARS), stop), daemon=True)
        for n in names
    ]
    print(f"\n  🤖 Launching {len(threads)} practice bots into mission {args.code.upper()}…")
    for t in threads:
        t.start()
        time.sleep(0.4)
    try:
        while any(t.is_alive() for t in threads):
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop.set()
        print("\n  Bots returning to base…")
        time.sleep(1.5)


if __name__ == "__main__":
    main()
