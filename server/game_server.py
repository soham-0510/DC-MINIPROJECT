"""
AstroQuiz Arena — RPC Game Server
=================================

This is the REMOTE OBJECT of the project (the equivalent of a Java RMI
`UnicastRemoteObject`). It is published with Pyro5:

    * Pyro5 Daemon       -> listens on a TCP port and dispatches calls
                            (like the RMI runtime / skeleton)
    * Pyro5 Name Server  -> optional registry: maps the logical name
                            "astroquiz.server" to the object's URI
                            (like `rmiregistry` + Naming.rebind)
    * Client Proxy       -> created by every Streamlit client
                            (like the RMI stub returned by Naming.lookup)

All game state (rooms, players, questions, scores, timers) lives here, so
every player sees exactly the same game. Clients only call methods.

Run:
    python game_server.py                 # direct mode, port 9100
    python game_server.py --ns            # also register with a Pyro5 Name Server
"""

from __future__ import annotations

import argparse
import random
import socket
import string
import threading
import time
import uuid
from collections import Counter, deque
from functools import wraps
from pathlib import Path
import sys

import Pyro5.api
import Pyro5.callcontext
import Pyro5.errors

sys.path.insert(0, str(Path(__file__).parent))

from models import (  # noqa: E402
    FINISHED, LAUNCH, LAUNCH_SECONDS, LOBBY, QUESTION, REVEAL, REVEAL_SECONDS,
    Player, Room,
)
from question_bank import DIFFICULTIES, QuestionBank  # noqa: E402
from scoring import POWERUPS, TIME_WARP_SECONDS, answer_points, rank_for  # noqa: E402

OBJECT_NAME = "astroquiz.server"
DEFAULT_PORT = 9100  # (9090 is the Pyro5 Name Server's default port)
SECTORS = [
    "ORION", "VEGA", "LYRA", "CYGNUS", "SIRIUS", "ANDROMEDA", "PERSEUS", "DRACO",
    "PHOENIX", "NOVA", "PEGASUS", "CASSIOPEIA", "RIGEL", "ALTAIR", "POLARIS", "HYDRA",
]
CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"  # no 0/O, 1/I/L confusion
MAX_PLAYERS = 12
ROOM_IDLE_TTL = 15 * 60
POLL_METHODS = {"get_room_state", "get_server_stats", "ping"}  # forget rooms nobody has polled for 15 minutes


def rpc_method(fn):
    """Decorator: logs every remote invocation (method, caller, latency) for the Ground Station."""

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        t0 = time.perf_counter()
        ok = True
        try:
            result = fn(self, *args, **kwargs)
            if isinstance(result, dict) and result.get("ok") is False:
                ok = False
            return result
        except Exception:
            ok = False
            raise
        finally:
            self._record_call(fn.__name__, args, (time.perf_counter() - t0) * 1000, ok)

    return wrapper


def ok(**data) -> dict:
    return {"ok": True, **data}


def fail(message: str) -> dict:
    return {"ok": False, "error": message}


@Pyro5.api.expose
@Pyro5.api.behavior(instance_mode="single")  # ONE shared remote object for every client
class AstroQuizServer:
    def __init__(self):
        self._lock = threading.RLock()  # Pyro5 serves each client on its own thread
        self._rooms: dict[str, Room] = {}
        self._bank = QuestionBank()
        self._started = time.time()
        self._log = deque(maxlen=300)      # every call, including polling
        self._events = deque(maxlen=150)   # only "action" calls (create, join, answer…)
        self._calls = Counter()
        self._clients: dict[str, float] = {}

    # ------------------------------------------------------------------ #
    #  Housekeeping (private — names starting with "_" are NOT exposed)   #
    # ------------------------------------------------------------------ #
    def _record_call(self, method: str, args: tuple, ms: float, ok_: bool) -> None:
        ctx = Pyro5.callcontext.current_context
        addr = getattr(ctx, "client_sock_addr", None)
        client = f"{addr[0]}:{addr[1]}" if addr else "local"
        arg_text = ", ".join(_short(a) for a in args)
        with self._lock:
            self._calls[method] += 1
            self._clients[client] = time.time()
            entry = {"t": time.time(), "method": method, "client": client,
                     "ms": round(ms, 2), "ok": ok_, "args": arg_text}
            self._log.append(entry)
            if method not in POLL_METHODS:
                self._events.append(entry)

    def _new_code(self) -> str:
        while True:
            code = "".join(random.choices(CODE_ALPHABET, k=6))
            if code not in self._rooms:
                return code

    def _room(self, code: str) -> Room | None:
        return self._rooms.get((code or "").strip().upper())

    def _purge(self) -> None:
        now = time.time()
        for code in list(self._rooms):
            room = self._rooms[code]
            last = max((p.last_seen for p in room.players.values()), default=room.created_at)
            if now - last > ROOM_IDLE_TTL:
                del self._rooms[code]

    def _ensure_host(self, room: Room) -> None:
        host = room.players.get(room.host_id)
        if host and (host.online or time.time() - host.last_seen < 15):
            return
        online = sorted((p for p in room.players.values() if p.online), key=lambda p: p.joined_at)
        if online:
            room.host_id = online[0].id

    def _player_deadline(self, room: Room, pid: str) -> float:
        return room.phase_started + room.time_per_q + room.warp.get(pid, 0)

    def _all_done(self, room: Room, now: float) -> bool:
        for pid, p in room.players.items():
            if room.q_index in p.answers or not p.online:
                continue
            if now < self._player_deadline(room, pid):
                return False
        return True

    def _start_question(self, room: Room, index: int, start: float) -> None:
        room.phase = QUESTION
        room.q_index = index
        room.phase_started = start
        room.phase_ends = start + room.time_per_q
        room.warp = {}
        room.hidden = {}

    def _reveal(self, room: Room, now: float) -> None:
        q = room.current_question
        for pid, p in room.players.items():
            ans = p.answers.get(room.q_index)
            if ans is None:
                ans = {"option": None, "time": None}
                p.answers[room.q_index] = ans
            correct = ans["option"] is not None and ans["option"] == q["answer"]
            ans["correct"] = correct
            ans["shielded"] = False
            if ans["option"] is not None:
                p.answered += 1
                p.total_time += ans["time"]
            if correct:
                p.streak += 1
                p.correct += 1
                p.best_streak = max(p.best_streak, p.streak)
                limit = room.time_per_q + room.warp.get(pid, 0)
                ans["points"] = answer_points(True, ans["time"], limit, p.streak)
                p.score += ans["points"]
            else:
                ans["points"] = 0
                if p.shield_active and p.streak > 0:
                    p.shield_active = False
                    ans["shielded"] = True  # streak survives
                else:
                    p.streak = 0
        room.score_history.append({pid: p.score for pid, p in room.players.items()})
        room.phase = REVEAL
        room.phase_started = now
        room.phase_ends = now + REVEAL_SECONDS

    def _tick(self, room: Room) -> None:
        """Advance the room's state machine using the server clock."""
        now = time.time()
        self._ensure_host(room)
        for _ in range(4):
            if room.phase == LAUNCH and now >= room.phase_ends:
                self._start_question(room, 0, room.phase_ends)
            elif room.phase == QUESTION and self._all_done(room, now):
                self._reveal(room, now)
            elif room.phase == REVEAL and now >= room.phase_ends:
                if room.q_index + 1 < len(room.questions):
                    self._start_question(room, room.q_index + 1, room.phase_ends)
                else:
                    room.phase = FINISHED
                    room.phase_started = now
                    room.phase_ends = None
                    room.games_played += 1
            else:
                break

    def _final_stats(self, room: Room) -> list[dict]:
        total = max(len(room.questions), 1)
        rows = []
        for p in room.players.values():
            accuracy = round(100 * p.correct / total)
            rows.append({
                **p.public(room.host_id),
                "correct": p.correct,
                "total": total,
                "accuracy": accuracy,
                "avg_time": round(p.total_time / p.answered, 2) if p.answered else None,
                "best_streak": p.best_streak,
                "powerups_used": [k for k, left in p.powerups.items() if not left],
                "rank": rank_for(accuracy),
            })
        rows.sort(key=lambda r: (-r["score"], -r["correct"], r["avg_time"] or 999))
        for i, r in enumerate(rows):
            r["place"] = i + 1
        return rows

    # ------------------------------------------------------------------ #
    #  REMOTE METHODS  (the RMI-style interface clients invoke)           #
    # ------------------------------------------------------------------ #
    @rpc_method
    def ping(self) -> dict:
        """Health check used by clients to show 'uplink' status and latency."""
        return ok(server="AstroQuiz Arena", time=time.time(), rooms=len(self._rooms))

    @rpc_method
    def get_categories(self) -> dict:
        return ok(categories=self._bank.category_list(), difficulties=["mixed"] + DIFFICULTIES)

    @rpc_method
    def create_room(self, name: str, avatar: str, category: str, difficulty: str,
                    num_questions: int, time_per_q: int) -> dict:
        name = (name or "").strip()[:18]
        if not name:
            return fail("Pick a callsign first.")
        valid = {c["id"] for c in self._bank.category_list()}
        if category not in valid:
            return fail("Unknown mission category.")
        if difficulty not in ["mixed"] + DIFFICULTIES:
            return fail("Unknown difficulty.")
        num_questions = int(max(3, min(20, num_questions)))
        time_per_q = int(max(5, min(60, time_per_q)))
        with self._lock:
            self._purge()
            code = self._new_code()
            host = Player(id=uuid.uuid4().hex[:10], name=name, avatar=avatar)
            room = Room(
                code=code, sector=random.choice(SECTORS), host_id=host.id,
                category=category, difficulty=difficulty,
                num_questions=num_questions, time_per_q=time_per_q,
            )
            room.players[host.id] = host
            self._rooms[code] = room
            return ok(code=code, player_id=host.id, sector=room.sector)

    @rpc_method
    def join_room(self, code: str, name: str, avatar: str) -> dict:
        name = (name or "").strip()[:18]
        if not name:
            return fail("Pick a callsign first.")
        with self._lock:
            room = self._room(code)
            if not room:
                return fail("No mission found with that code. Check the code and try again.")
            if room.phase != LOBBY:
                return fail("That mission has already launched. Ask the host to start a new one.")
            if len(room.players) >= MAX_PLAYERS:
                return fail(f"The crew is full ({MAX_PLAYERS} astronauts max).")
            taken = {p.name.lower() for p in room.players.values()}
            base, n = name, 2
            while name.lower() in taken:
                name = f"{base[:15]}-{n}"
                n += 1
            player = Player(id=uuid.uuid4().hex[:10], name=name, avatar=avatar)
            room.players[player.id] = player
            return ok(code=room.code, player_id=player.id, sector=room.sector, name=name)

    @rpc_method
    def update_settings(self, code: str, player_id: str, category: str, difficulty: str,
                        num_questions: int, time_per_q: int) -> dict:
        with self._lock:
            room = self._room(code)
            if not room or room.host_id != player_id:
                return fail("Only the host can change mission settings.")
            if room.phase not in (LOBBY, FINISHED):
                return fail("Settings are locked while a mission is running.")
            room.category = category
            room.difficulty = difficulty
            room.num_questions = int(max(3, min(20, num_questions)))
            room.time_per_q = int(max(5, min(60, time_per_q)))
            return ok()

    @rpc_method
    def start_game(self, code: str, player_id: str) -> dict:
        with self._lock:
            room = self._room(code)
            if not room:
                return fail("Mission not found.")
            if room.host_id != player_id:
                return fail("Only the mission host can launch.")
            if room.phase not in (LOBBY, FINISHED):
                return fail("Mission already in flight.")
            room.questions = self._bank.build_set(room.category, room.difficulty, room.num_questions)
            for p in room.players.values():
                p.reset_for_new_game()
            room.score_history = []
            room.q_index = -1
            room.phase = LAUNCH
            room.phase_started = time.time()
            room.phase_ends = room.phase_started + LAUNCH_SECONDS
            return ok()

    @rpc_method
    def submit_answer(self, code: str, player_id: str, q_index: int, option: int) -> dict:
        with self._lock:
            room = self._room(code)
            if not room or player_id not in room.players:
                return fail("You are not part of this mission.")
            self._tick(room)
            if room.phase != QUESTION or room.q_index != q_index:
                return fail("Too late — that question has closed.")
            player = room.players[player_id]
            if q_index in player.answers:
                return fail("Answer already transmitted.")
            now = time.time()
            if now > self._player_deadline(room, player_id) + 0.75:
                return fail("Time's up!")
            if option not in range(4) or option in room.hidden.get(player_id, []):
                return fail("Invalid option.")
            player.answers[q_index] = {"option": int(option), "time": round(now - room.phase_started, 3)}
            self._tick(room)  # maybe everyone has answered -> reveal right away
            # NOTE: correctness is NOT returned here — it is revealed to everyone together.
            return ok(received=True)

    @rpc_method
    def use_powerup(self, code: str, player_id: str, powerup: str) -> dict:
        with self._lock:
            room = self._room(code)
            if not room or player_id not in room.players:
                return fail("You are not part of this mission.")
            self._tick(room)
            player = room.players[player_id]
            if powerup not in POWERUPS:
                return fail("Unknown power-up.")
            if not player.powerups.get(powerup):
                return fail("Power-up already used this mission.")
            if powerup == "shield":
                if room.phase not in (QUESTION, REVEAL, LAUNCH):
                    return fail("Shields can only be raised during a mission.")
                player.shield_active = True
            else:
                if room.phase != QUESTION or room.q_index in player.answers:
                    return fail("Use this while a question is live.")
                if powerup == "black_hole":
                    wrong = [i for i in range(4) if i != room.current_question["answer"]]
                    room.hidden[player_id] = random.sample(wrong, 2)
                elif powerup == "time_warp":
                    room.warp[player_id] = room.warp.get(player_id, 0) + TIME_WARP_SECONDS
            player.powerups[powerup] = False
            return ok(powerup=powerup, hidden=room.hidden.get(player_id, []))

    @rpc_method
    def get_room_state(self, code: str, player_id: str) -> dict:
        """Polled ~once a second by every client: the single source of truth."""
        with self._lock:
            room = self._room(code)
            if not room:
                return fail("Mission not found — it may have expired.")
            me = room.players.get(player_id)
            if not me:
                return fail("You are no longer part of this mission.")
            me.last_seen = time.time()
            self._tick(room)
            now = time.time()

            players = sorted(
                (p.public(room.host_id) for p in room.players.values()),
                key=lambda x: (-x["score"], x["name"].lower()),
            )
            state = {
                "code": room.code,
                "sector": room.sector,
                "phase": room.phase,
                "host_id": room.host_id,
                "is_host": room.host_id == player_id,
                "settings": room.settings(),
                "category_title": self._bank.title_for(room.category),
                "category_icon": self._bank.icon_for(room.category),
                "players": players,
                "q_index": room.q_index,
                "total_q": len(room.questions) or room.num_questions,
                "games_played": room.games_played,
                "me": {
                    **me.public(room.host_id),
                    "powerups": dict(me.powerups),
                    "correct": me.correct,
                },
            }
            if room.phase == LAUNCH:
                state["time_left"] = max(0.0, room.phase_ends - now)
                state["duration"] = LAUNCH_SECONDS

            if room.phase in (QUESTION, REVEAL):
                q = room.current_question
                state["question"] = {
                    "text": q["question"],
                    "options": q["options"],
                    "difficulty": q["difficulty"],
                    "category": q["category"],
                    "category_title": self._bank.title_for(q["category"]),
                    "category_icon": self._bank.icon_for(q["category"]),
                    "visual": q.get("visual"),
                }

            if room.phase == QUESTION:
                limit = room.time_per_q + room.warp.get(player_id, 0)
                state["duration"] = limit
                state["elapsed"] = now - room.phase_started
                state["time_left"] = max(0.0, self._player_deadline(room, player_id) - now)
                state["hidden"] = room.hidden.get(player_id, [])
                state["warp"] = room.warp.get(player_id, 0)
                mine = me.answers.get(room.q_index)
                state["my_answer"] = mine["option"] if mine else None
                state["answered_ids"] = [pid for pid, p in room.players.items() if room.q_index in p.answers]

            if room.phase == REVEAL:
                q = room.current_question
                state["time_left"] = max(0.0, room.phase_ends - now)
                state["duration"] = REVEAL_SECONDS
                state["reveal"] = {
                    "answer": q["answer"],
                    "fact": q.get("fact", ""),
                    "results": [
                        {
                            "id": pid, "name": p.name, "avatar": p.avatar,
                            **{k: p.answers[room.q_index].get(k) for k in ("option", "correct", "points", "time", "shielded")},
                        }
                        for pid, p in room.players.items()
                    ],
                }
                state["my_answer"] = me.answers.get(room.q_index, {}).get("option")
                state["prev_scores"] = room.score_history[-2] if len(room.score_history) > 1 else {}

            if room.phase == FINISHED:
                state["final"] = self._final_stats(room)
                state["history"] = room.score_history
            return ok(state=state)

    @rpc_method
    def play_again(self, code: str, player_id: str) -> dict:
        """Host sends the crew back to the lobby (same room, same players)."""
        with self._lock:
            room = self._room(code)
            if not room or room.host_id != player_id:
                return fail("Only the host can reset the mission.")
            room.phase = LOBBY
            room.q_index = -1
            room.questions = []
            room.score_history = []
            for p in room.players.values():
                p.reset_for_new_game()
            return ok()

    @rpc_method
    def leave_room(self, code: str, player_id: str) -> dict:
        with self._lock:
            room = self._room(code)
            if room and player_id in room.players:
                del room.players[player_id]
                if not room.players:
                    del self._rooms[room.code]
                else:
                    self._ensure_host(room)
                    if room.host_id == player_id:
                        room.host_id = min(room.players.values(), key=lambda p: p.joined_at).id
            return ok()

    @rpc_method
    def get_server_stats(self) -> dict:
        """Everything the Ground Station (server monitor) page shows."""
        with self._lock:
            now = time.time()
            rooms = []
            for room in self._rooms.values():
                self._tick(room)
                rooms.append({
                    "code": room.code,
                    "sector": room.sector,
                    "phase": room.phase,
                    "category": self._bank.title_for(room.category),
                    "icon": self._bank.icon_for(room.category),
                    "players": len(room.players),
                    "online": sum(p.online for p in room.players.values()),
                    "question": f"{max(room.q_index + 1, 0)}/{len(room.questions) or room.num_questions}",
                    "age_s": int(now - room.created_at),
                })
            return ok(
                uptime_s=int(now - self._started),
                total_calls=sum(self._calls.values()),
                calls_by_method=dict(self._calls),
                active_clients=sum(1 for t in self._clients.values() if now - t < 10),
                rooms=rooms,
                players_online=sum(r["online"] for r in rooms),
                log=list(self._log)[-80:],
                events=list(self._events)[-80:],
                server_time=now,
            )


def _short(value, limit: int = 24) -> str:
    text = repr(value)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def lan_ip() -> str:
    """Best-effort LAN IP so other machines on the Wi-Fi can reach us."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")  # emoji-safe on any Windows console
    parser = argparse.ArgumentParser(description="AstroQuiz Arena RPC game server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="TCP port (default 9100)")
    parser.add_argument("--host", default=None, help="IP address clients use to reach this server (auto-detected)")
    parser.add_argument("--ns", action="store_true", help="register with a running Pyro5 Name Server")
    parser.add_argument("--ns-host", default=None, help="Name Server address (default: auto-discover)")
    args = parser.parse_args()

    public_ip = args.host or lan_ip()
    # Listen on all interfaces, but advertise the LAN IP inside the object's URI.
    daemon = Pyro5.api.Daemon(host="0.0.0.0", port=args.port, nathost=public_ip, natport=args.port)
    server = AstroQuizServer()
    uri = daemon.register(server, objectId=OBJECT_NAME)

    registered = False
    if args.ns:
        try:
            ns = Pyro5.api.locate_ns(host=args.ns_host)
            ns.register(OBJECT_NAME, uri)
            registered = True
        except Pyro5.errors.NamingError:
            print("  ! Name Server not found — start it first with:  python -m Pyro5.nameserver -n 0.0.0.0")

    line = "═" * 62
    print(f"\n{line}")
    print("  🚀  AstroQuiz Arena — RPC Game Server is ONLINE")
    print(line)
    print(f"  Remote object : {OBJECT_NAME}")
    print(f"  URI           : {uri}")
    print(f"  Same computer : connect to   localhost:{args.port}")
    print(f"  Other devices : connect to   {public_ip}:{args.port}")
    if registered:
        print(f"  Name Server   : registered as PYRONAME:{OBJECT_NAME}")
    print(f"  Questions     : {sum(c['count'] for c in server._bank.category_list()[1:])} across "
          f"{len(server._bank.categories)} categories")
    print(f"{line}\n  Waiting for astronauts…  (Ctrl+C to stop)\n")
    try:
        daemon.requestLoop()
    except KeyboardInterrupt:
        print("\n  Server shutting down. Clear skies! 🌌")
    finally:
        if registered:
            try:
                Pyro5.api.locate_ns(host=args.ns_host).remove(OBJECT_NAME)
            except Exception:
                pass
        daemon.close()


if __name__ == "__main__":
    main()
