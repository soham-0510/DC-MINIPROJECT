# 🚀 AstroQuiz Arena — Multiplayer Space Quiz using RMI/RPC

A real-time multiplayer quiz game about **space & astronomy**, built with **Streamlit** (UI) and
**Pyro5** (Python Remote Objects — Python's equivalent of Java RMI).

One **game server** holds a single shared *remote object*. Every player's Streamlit app is an
**RPC client** that calls methods on it — `create_room()`, `join_room()`, `submit_answer()`,
`get_room_state()` — exactly as if the object were local.

---

## ✨ Features

| Area | What you get |
|---|---|
| Multiplayer | Rooms with 6-character codes, up to 12 astronauts, host controls, auto host hand-over, refresh-safe sessions |
| Game | 119 questions in 6 categories (Solar System, Stars & Galaxies, Black Holes & Cosmology, Space Missions, **ISRO Special**, **Visual Round**) + Random Galaxy mix |
| Scoring | 100 pts + up to 50 speed bonus, ×1.5 streak multiplier from 3 in a row, ranks from Space Cadet to Galactic Legend |
| Power-ups | 🕳️ Black Hole (removes 2 wrong options), ⏳ Time Warp (+5 s), 🛡️ Force Shield (saves your streak) |
| Fair play | The server owns the clock, and the correct answer is **never sent** to clients until everyone has answered |
| Animations | Parallax starfield + shooting stars, orbiting planet hero, beam-in crew cards, 3-2-1 rocket launch, warp-speed question transitions, orbit-ring timer, supernova / asteroid-impact answer reveals, rocket-race leaderboard, rising podium with star confetti |
| UI | Deep-space glass theme, shadcn components (`streamlit-shadcn-ui`), bundled Orbitron + Space Grotesk fonts (works offline), responsive down to phones |
| Ground Station | Live server monitor: uptime, connected clients, active rooms, and a live log of every remote call |
| Extras | Practice bots for solo demos, Pyro5 Name Server support (RMI-registry style lookup), unit tests |

---

## 🧰 Requirements

* Python **3.10+**
* Install packages (once):

```bash
pip install -r requirements.txt
```

---

## ▶️ How to run

Open **two terminals** in the project folder (the folder with this README):

```bash
# Terminal 1 — the RPC game server (remote object)
python server/game_server.py

# Terminal 2 — the Streamlit client
streamlit run client/app.py
```

The browser opens at `http://localhost:8501`. Open more tabs (or other devices) to add players.

> **Windows shortcut:** double-click `scripts\start_all.bat` — it opens the Name Server,
> the game server and the client in three windows. (`scripts/start_all.sh` on Linux/macOS.)

### Play with friends on the same Wi-Fi

1. Run the server and client on one laptop (the "host" machine).
2. Streamlit prints a **Network URL** such as `http://192.168.1.20:8501`.
   Friends open that URL on their phones/laptops — no installation needed on their side.
3. Host clicks **Plan a new mission** → **Create mission**, and shares the 6-character code.
4. Everyone else enters the code under **Join a crew**.

If friends run their **own** Streamlit client on their laptops, they open **Uplink** (top bar)
and enter the host's IP (`192.168.1.20`) and port `9100`.

> Windows may show a firewall prompt for Python — click **Allow** (private networks) so ports
> **8501** (Streamlit) and **9100** (game server) are reachable.

### Practise alone with bots

Create a mission, then in a third terminal:

```bash
python server/bots.py ABC123 --count 3      # ABC123 = your mission code
```

Each bot is a separate RPC client that joins, polls and answers like a real player.

### Using the Name Server (RMI-registry style)

```bash
python -m Pyro5.nameserver -n 0.0.0.0       # like `rmiregistry`   (port 9090)
python server/game_server.py --ns           # registers "astroquiz.server" (like Naming.rebind)
streamlit run client/app.py
```

In the app, open **Uplink** → turn on **Find the server through the Pyro5 Name Server**. The client
now looks the object up **by name** (`PYRONAME:astroquiz.server`) instead of by address.

---

## 🏗️ Architecture

```
   Browser tabs / phones
          │  (Streamlit websocket)
          ▼
 ┌─────────────────────────┐        lookup by name (optional)      ┌──────────────────────┐
 │  Streamlit client       │ ────────────────────────────────────▶ │  Pyro5 Name Server    │
 │  client/app.py          │                                        │  "astroquiz.server"   │
 │  rpc.py → Pyro5 Proxy   │ ◀──── URI ──────────────────────────── │  (≈ rmiregistry)      │
 │  (≈ RMI stub)           │                                        └──────────────────────┘
 └───────────┬─────────────┘
             │  remote method calls over TCP (port 9100)
             ▼
 ┌──────────────────────────────────────────────────────────┐
 │  Pyro5 Daemon (≈ RMI runtime / skeleton)                 │
 │      └── AstroQuizServer  — ONE shared remote object     │
 │           rooms · players · questions · timers · scores  │
 │           threading.RLock (each client call = 1 thread)  │
 └──────────────────────────────────────────────────────────┘
```

**Why polling?** A Streamlit page can't receive pushes from another server, so the live screen is
a Streamlit *fragment* that calls `get_room_state()` once per second. Animations are pure CSS, so
they stay smooth between polls.

### Remote interface (`server/game_server.py`)

| Method | Purpose |
|---|---|
| `ping()` | health check + latency |
| `get_categories()` | mission types and question counts |
| `create_room(name, avatar, category, difficulty, n, seconds)` | host a mission → code + player id |
| `join_room(code, name, avatar)` | join a mission |
| `update_settings(code, pid, …)` | host edits the mission |
| `start_game(code, pid)` | host launches |
| `get_room_state(code, pid)` | the single source of truth, polled every second |
| `submit_answer(code, pid, q_index, option)` | send an answer (correctness is *not* returned) |
| `use_powerup(code, pid, name)` | Black Hole / Time Warp / Force Shield |
| `play_again(code, pid)` | host returns the crew to the lobby |
| `leave_room(code, pid)` | leave (host role passes on automatically) |
| `get_server_stats()` | data for the Ground Station page |

### Game state machine (server-side clock)

```
LOBBY ──start_game──▶ LAUNCH (4 s) ──▶ QUESTION ──all answered / time up──▶ REVEAL (6 s) ──▶ next QUESTION … ──▶ FINISHED
  ▲                                                                                                             │
  └──────────────────────────────────────────── play_again ─────────────────────────────────────────────────────┘
```

---

## 📁 Project structure

```
astroquiz_arena/
├── server/
│   ├── game_server.py        # Pyro5 remote object + daemon + Name Server registration
│   ├── models.py             # Room / Player data + phases
│   ├── scoring.py            # points, streaks, power-ups, ranks
│   ├── question_bank.py      # loads & shuffles questions
│   ├── bots.py               # practice bots (extra RPC clients)
│   └── data/questions/*.json # 119 questions with fun facts
├── client/
│   ├── app.py                # Streamlit entry: page setup, top bar, routing
│   ├── rpc.py                # Pyro5 proxy wrapper (the stub side)
│   ├── theme.py              # design tokens, starfield, all CSS animations
│   ├── views/                # home · setup · live (lobby/game/podium) · ground_station
│   ├── components/           # HTML widgets + SVG art for the Visual Round
│   └── static/fonts/         # Orbitron + Space Grotesk (OFL), served locally
├── tests/test_game_server.py # game-logic tests (no network needed)
├── scripts/                  # one-click start scripts (Windows .bat, Linux/macOS .sh)
├── docs/VIVA_NOTES.md        # how RMI/RPC concepts map to this code + likely viva questions
├── .streamlit/config.toml    # dark theme, static file serving
└── requirements.txt
```

Run the tests with `python tests/test_game_server.py` (or `python -m pytest tests -q`).

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| Red dot / "Can't reach the game server" | Start `python server/game_server.py` first, then check **Uplink** host & port (default `localhost:9100`). |
| Friends can't open the Network URL | Same Wi-Fi? Allow Python through the firewall. College Wi-Fi sometimes blocks device-to-device traffic — use a phone hotspot. |
| "Address already in use" | Another server is running on that port. Close it, or run `python server/game_server.py --port 9200` and set the port in **Uplink**. |
| Theme looks plain | Run Streamlit **from the project folder** so `.streamlit/config.toml` is picked up. |
| `--ns` says Name Server not found | Start `python -m Pyro5.nameserver -n 0.0.0.0` before the game server. |
