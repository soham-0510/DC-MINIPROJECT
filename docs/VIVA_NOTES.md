# Viva notes — AstroQuiz Arena (Multiplayer Quiz using RMI/RPC)

## 1. One-line summary
A multiplayer space quiz where a single **remote object** on a game server holds all game state,
and every player's **Streamlit** app talks to it through **remote method invocation** using
**Pyro5** (Python Remote Objects).

## 2. RMI / RPC concepts → where they are in the code

| Concept (Java RMI term) | In this project | File |
|---|---|---|
| Remote interface | Public methods of `AstroQuizServer` exposed with `@Pyro5.api.expose` | `server/game_server.py` |
| Remote object (`UnicastRemoteObject`) | `AstroQuizServer` instance, `instance_mode="single"` so all clients share it | `server/game_server.py` |
| RMI runtime / skeleton | `Pyro5.api.Daemon` — listens on TCP 9100, unpacks calls, dispatches them | `main()` in `game_server.py` |
| Registry (`rmiregistry`) | Pyro5 Name Server (`python -m Pyro5.nameserver`) | `--ns` flag |
| `Naming.rebind(name, obj)` | `ns.register("astroquiz.server", uri)` | `main()` |
| `Naming.lookup(name)` | `Proxy("PYRONAME:astroquiz.server@host")` | `client/rpc.py` |
| Stub | `Pyro5.api.Proxy` — looks like a local object, forwards calls over the network | `client/rpc.py` |
| Marshalling / serialization | Pyro5 serializes arguments & return values with *serpent* (only plain dicts/lists/str/int travel) | everywhere |
| `RemoteException` | `Pyro5.errors.CommunicationError` → shown as a friendly "uplink lost" message | `client/rpc.py` |
| Concurrency on the server | Each client call runs on its own thread → shared state protected by `threading.RLock` | `game_server.py` |

## 3. How one answer travels (good to explain on the whiteboard)
1. Player clicks option **B** in the browser.
2. Streamlit runs `on_answer()` → `rpc.call("submit_answer", code, pid, q_index, 1)`.
3. The Pyro5 **proxy** serializes the call and sends it over TCP to the daemon on port 9100.
4. The daemon invokes `AstroQuizServer.submit_answer(...)` on a worker thread.
5. The server locks the room, records the answer and the server-side time taken, and returns
   `{"ok": True, "received": True}` — **not** whether it was correct.
6. Every client's fragment calls `get_room_state()` each second. When all players have answered (or
   time is up) the server moves to **REVEAL**, and the next poll returns the answer and the scores
   to everyone at the same moment.

## 4. Design decisions worth mentioning
* **Server owns the clock.** Clients only display time; the server decides when a question ends,
  so refreshing the page or a slow phone can't buy extra time.
* **No cheating via the network.** The correct answer index is never sent while a question is live.
* **Stateless clients.** If a browser refreshes, the room code and player id in the URL restore
  the session — the game continues because the state lives on the server.
* **Polling instead of callbacks.** Pyro5 supports callbacks, but a Streamlit page can't receive
  them, so clients poll `get_room_state()` once a second (cheap: well under 1 ms per call on a LAN).
* **Host hand-over.** If the host leaves or goes silent for 15 s, the next astronaut becomes host.
* **Speed bonus measured on the server**, not trusted from the client.

## 5. Likely viva questions (with short answers)
* **RMI vs RPC?** RPC calls remote *procedures*; RMI calls methods on remote *objects* and can pass
  object references. Pyro5 is object-oriented like RMI, and also works as plain RPC.
* **Why Pyro5 instead of Java RMI?** The UI is Streamlit (Python), so we need a Python RMI system.
  Pyro5 has the same building blocks: remote objects, a daemon, a name server and proxies.
* **What happens if two players answer at the same time?** Both calls arrive on separate daemon
  threads; the `RLock` serializes access to the room, so both answers are recorded safely.
* **What if the server crashes?** Clients show a red uplink indicator and keep retrying; the game
  state would be lost because it is kept in memory (a database could be added for persistence).
* **How is latency shown?** `rpc.call()` times every round-trip; the top bar shows it in ms.
* **How do you see the RPC traffic?** The **Ground Station** page shows every call (method,
  caller IP:port, latency) using the `get_server_stats()` remote method.
* **Scalability?** One daemon handles many clients with a thread pool; rooms are independent, so
  it scales to a classroom easily. For more, rooms could be sharded across several servers and
  located through the Name Server.

## 6. Live demo script (3 minutes)
1. Start the server; point at the banner: object name, URI, port.
2. Open the app, show the hero animation, create a **Visual Round** mission.
3. Join from a phone using the Network URL + code (or `python server/bots.py CODE`).
4. Launch → rocket countdown → answer a question → show the reveal and rocket race.
5. Use **Black Hole** to show a power-up handled server-side.
6. Open **Ground Station** in another tab: the live RPC log shows `submit_answer` calls arriving
   from different client ports.
7. Finish → podium + mission trajectory chart.
