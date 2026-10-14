"""
The live mission: lobby → launch → questions → reveals → podium.

The whole screen is a Streamlit *fragment* that re-runs every second and
polls `get_room_state()` over RPC. The server owns the clock and the state
machine; this file only draws what the server says.
"""

from __future__ import annotations

import plotly.graph_objects as go_
import streamlit as st
import streamlit_shadcn_ui as ui

import rpc
from components import widgets as W
from views.setup import DIFF_NAMES, DIFFS

POWERUP_INFO = {
    "black_hole": ("🕳️", "Black Hole", "Swallows two wrong answers"),
    "time_warp": ("⏳", "Time Warp", "+5 seconds on your clock"),
    "shield": ("🛡️", "Force Shield", "Saves your streak from one miss"),
}


# ---------------------------------------------------------------- helpers
def stable(key, value):
    """Remember the first value seen for `key` so animation markup stays identical across polls."""
    anim = st.session_state.anim
    if key not in anim:
        anim[key] = value
        if len(anim) > 200:
            for k in list(anim)[:100]:
                anim.pop(k, None)
    return anim[key]


def leave(go) -> None:
    ss = st.session_state
    if ss.code and ss.pid:
        rpc.call("leave_room", ss.code, ss.pid)
    ss.code = ss.pid = None
    st.query_params.clear()
    go("home")


def flash_box() -> None:
    msg = st.session_state.get("live_flash")
    if msg:
        st.markdown(W.alert(msg), unsafe_allow_html=True)
        st.session_state.live_flash = None


# ---------------------------------------------------------------- callbacks (run before the fragment re-runs)
def on_answer(q_index: int, option: int) -> None:
    ss = st.session_state
    res = rpc.call("submit_answer", ss.code, ss.pid, q_index, option)
    if not res.get("ok"):
        ss.live_flash = res.get("error")


def on_powerup(name: str) -> None:
    ss = st.session_state
    res = rpc.call("use_powerup", ss.code, ss.pid, name)
    if not res.get("ok"):
        ss.live_flash = res.get("error")


def on_start() -> None:
    ss = st.session_state
    res = rpc.call("start_game", ss.code, ss.pid)
    if not res.get("ok"):
        ss.live_flash = res.get("error")


def on_play_again() -> None:
    ss = st.session_state
    res = rpc.call("play_again", ss.code, ss.pid)
    if not res.get("ok"):
        ss.live_flash = res.get("error")


# ---------------------------------------------------------------- lobby
def lobby(state: dict, go) -> None:
    ss = st.session_state
    me_id = ss.pid
    players = sorted(state["players"], key=lambda p: p.get("joined_at", 0))
    host = next((p for p in players if p["is_host"]), None)

    left, right = st.columns([1.25, 1], gap="large")
    with left:
        with st.container(key="card_mission"):
            st.markdown(W.code_display(state["code"], state["sector"]), unsafe_allow_html=True)
            with st.container(key="copycode"):
                st.code(state["code"], language=None)
            st.markdown(
                '<div class="section-sub" style="text-align:center">Crewmates open AstroQuiz on the same network, '
                'choose <b>Join a crew</b> and type this code.</div>', unsafe_allow_html=True)
            st.markdown(W.settings_chips(state["settings"], state["category_title"], state["category_icon"]),
                        unsafe_allow_html=True)
            st.write("")
            if state["is_host"]:
                c1, c2 = st.columns([1, 1.6], vertical_alignment="center")
                with c1:
                    with st.popover("⚙️ Mission settings", width="stretch"):
                        edit_settings(state)
                with c2:
                    with st.container(key="launch_btn"):
                        label = "LAUNCH MISSION" if len(players) > 1 else "LAUNCH SOLO"
                        st.button(label, type="primary", width="stretch", key="btn_launch", on_click=on_start)
                if len(players) == 1:
                    st.markdown('<div class="section-sub" style="margin-top:10px">Waiting for your crew? '
                                'Share the code — or launch solo to practise.</div>', unsafe_allow_html=True)
            else:
                host_name = W.esc(host["name"]) if host else "the host"
                st.markdown(W.loader(f"Standing by. <b>{host_name}</b> will launch the mission when the crew is ready."),
                            unsafe_allow_html=True)
        flash_box()
        st.button("Leave mission", type="tertiary", key="btn_leave_lobby", on_click=leave, args=(go,))

    with right:
        with st.container(key="card_crew"):
            online = sum(1 for p in players if p.get("online", True))
            st.markdown(W.section(f"Crew manifest · {len(players)}/12", f"{online} on the uplink"),
                        unsafe_allow_html=True)
            # One element per astronaut: a newcomer beams in without replaying everyone else's animation
            for p in players:
                st.markdown(W.crew_card(p, me_id), unsafe_allow_html=True)
            if len(players) < 12:
                st.markdown(f'<div style="margin-top:6px">{W.loader("Scanning for incoming astronauts…")}</div>',
                            unsafe_allow_html=True)


def edit_settings(state: dict) -> None:
    ss = st.session_state
    s = state["settings"]
    cats = ss.get("_cats") or rpc.call("get_categories").get("categories", [])
    ss["_cats"] = cats
    ids = [c["id"] for c in cats]
    names = {c["id"]: f"{c['icon']}  {c['title']}" for c in cats}
    cat = st.selectbox("Mission type", ids, index=ids.index(s["category"]) if s["category"] in ids else 0,
                       format_func=lambda i: names[i], key="edit_cat")
    diff = st.selectbox("Difficulty", DIFFS, index=DIFFS.index(s["difficulty"]), format_func=lambda d: DIFF_NAMES[d],
                        key="edit_diff")
    n = st.slider("Questions", 3, 20, s["num_questions"], key="edit_n")
    t = st.slider("Seconds per question", 10, 30, s["time_per_q"], step=5, key="edit_t")
    if st.button("Save settings", type="primary", width="stretch", key="edit_save"):
        res = rpc.call("update_settings", ss.code, ss.pid, cat, diff, n, t)
        if not res.get("ok"):
            ss.live_flash = res.get("error")
        st.rerun(scope="fragment")


# ---------------------------------------------------------------- question + reveal
def question_view(state: dict) -> None:
    ss = st.session_state
    phase = state["phase"]
    q = state["question"]
    qi = state["q_index"]
    me = state["me"]
    players = state["players"]

    if phase == "question":
        st.markdown(W.warp(qi), unsafe_allow_html=True)
    else:
        st.markdown("", unsafe_allow_html=True)  # keeps element positions stable between phases

    st.markdown(W.game_bar(state), unsafe_allow_html=True)
    main, side = st.columns([2.25, 1], gap="large")

    with main:
        qcol, tcol = st.columns([5, 1.1], vertical_alignment="center")
        with qcol:
            st.markdown(W.question_card(state), unsafe_allow_html=True)
        with tcol:
            if phase == "question":
                elapsed0 = stable(("q", ss.code, state["games_played"], qi, state.get("warp", 0)),
                                  state["duration"] - state["time_left"])
                st.markdown(W.timer(qi, state["duration"], elapsed0, state.get("warp", 0)), unsafe_allow_html=True)
            else:
                st.markdown(W.one_line("""<div class="timer"><svg viewBox="0 0 104 104"><circle class="track" cx="52" cy="52" r="44"/>
                    </svg><div class="num" style="font-size:2.2rem">✦</div></div>"""), unsafe_allow_html=True)

        st.write("")
        if phase == "question":
            answer_area(state)
        else:
            reveal_area(state)

    with side:
        with st.container(key="card_race"):
            if phase == "question":
                answered = set(state.get("answered_ids", []))
                st.markdown(W.section("Rocket race", f"{len(answered)} of {len(players)} answers in"),
                            unsafe_allow_html=True)
                st.markdown(W.race(players, ss.pid, answered_ids=answered), unsafe_allow_html=True)
            else:
                prev = state.get("prev_scores") or {}
                deltas = {r["id"]: r["points"] for r in state["reveal"]["results"] if r.get("points")}
                st.markdown(W.section("Rocket race", "Scores just landed"), unsafe_allow_html=True)
                st.markdown(W.race(players, ss.pid, prev_scores=prev, animate=True, deltas=deltas),
                            unsafe_allow_html=True)
        if phase == "question":
            st.markdown(f'<div class="section-sub" style="margin-top:10px;text-align:center">'
                        f'Uplink {ss.get("last_latency_ms") or 0:.0f} ms · Sector {W.esc(state["sector"])} · '
                        f'{W.esc(state["code"])}</div>', unsafe_allow_html=True)


def answer_area(state: dict) -> None:
    q = state["question"]
    qi = state["q_index"]
    hidden = set(state.get("hidden", []))
    chosen = state.get("my_answer")
    time_up = state["time_left"] <= 0.05

    if chosen is not None:
        st.markdown(W.options_html(q["options"], "locked", chosen=chosen, hidden=hidden), unsafe_allow_html=True)
        waiting = len(state["players"]) - len(state.get("answered_ids", []))
        msg = "Answer locked in." + (f" Waiting for {waiting} more crew…" if waiting > 0 else " Revealing…")
        st.markdown(f'<div style="margin-top:14px">{W.loader(msg)}</div>', unsafe_allow_html=True)
    elif time_up:
        st.markdown(W.options_html(q["options"], "timeout", hidden=hidden), unsafe_allow_html=True)
        st.markdown(f'<div style="margin-top:14px">{W.loader("Time is up — waiting for the rest of the crew…")}</div>',
                    unsafe_allow_html=True)
    else:
        with st.container(key="answers"):
            for row in (0, 2):
                cols = st.columns(2, gap="small")
                for j, col in enumerate(cols):
                    i = row + j
                    with col:
                        with st.container(key=f"opt{i}_q{qi}"):
                            st.button(q["options"][i], key=f"ans_{qi}_{i}", width="stretch",
                                      disabled=i in hidden, on_click=on_answer, args=(qi, i))
        powerups(state)
    flash_box()


def powerups(state: dict) -> None:
    me = state["me"]
    left = me.get("powerups", {})
    st.markdown('<div class="section-sub" style="margin:14px 0 6px">Power-ups · one use each per mission</div>',
                unsafe_allow_html=True)
    row = st.container(horizontal=True, gap="small", key="powerups")
    for key, (icon, name, desc) in POWERUP_INFO.items():
        with row:
            with st.container(key=f"pu_{key}"):
                active = key == "shield" and me.get("shield_active")
                label = f"{icon}  {name}" + (" · active" if active else "" if left.get(key) else " · used")
                st.button(label, key=f"btn_pu_{key}", width="stretch", help=desc,
                          disabled=not left.get(key), on_click=on_powerup, args=(key,))


def reveal_area(state: dict) -> None:
    ss = st.session_state
    q = state["question"]
    rv = state["reveal"]
    answer = rv["answer"]
    results = rv["results"]
    mine = next((r for r in results if r["id"] == ss.pid), None)
    counts = {}
    for r in results:
        if r.get("option") is not None:
            counts[r["option"]] = counts.get(r["option"], 0) + 1
    st.markdown(W.options_html(q["options"], "reveal", chosen=state.get("my_answer"), answer=answer,
                               pick_counts=counts), unsafe_allow_html=True)
    st.write("")
    st.markdown(W.result_banner(mine, q["options"][answer], W.LETTERS[answer], state["me"]["streak"]),
                unsafe_allow_html=True)
    st.markdown(W.fact(rv.get("fact", "")), unsafe_allow_html=True)
    last = state["q_index"] + 1 >= state["total_q"]
    secs = stable(("rv", ss.code, state["games_played"], state["q_index"]), state["time_left"])
    st.markdown(W.next_bar("Final results incoming…" if last else "Next question incoming…", secs,
                           f"{state['q_index']}"), unsafe_allow_html=True)


# ---------------------------------------------------------------- results
def finished_view(state: dict, go) -> None:
    ss = st.session_state
    final = state["final"]
    me = next((r for r in final if r["id"] == ss.pid), final[0])
    st.html(W.confetti_script(f"{ss.code}-{state['games_played']}"), unsafe_allow_javascript=True)

    st.markdown(W.one_line(f"""<div style="text-align:center;margin-top:6px">
        <h2 style="margin:0;font-size:clamp(1.8rem,4vw,2.6rem);animation:rise .8s var(--ease-out) both">Mission complete</h2>
        <div class="section-sub" style="animation:rise .8s var(--ease-out) .1s both">
        {W.esc(state['category_icon'])} {W.esc(state['category_title'])} · Sector {W.esc(state['sector'])}</div></div>"""),
        unsafe_allow_html=True)
    st.markdown(W.podium(final), unsafe_allow_html=True)
    st.write("")

    left, right = st.columns([1, 1.35], gap="large")
    with left:
        st.markdown(W.rank_card(me), unsafe_allow_html=True)
        st.markdown(W.stats(me), unsafe_allow_html=True)
        st.write("")
        if state["is_host"]:
            with st.container(key="launch_again"):
                st.button("FLY AGAIN WITH THIS CREW", type="primary", width="stretch", key="btn_again",
                          on_click=on_play_again)
        else:
            st.markdown(W.loader("The host can start another mission with this crew."), unsafe_allow_html=True)
        st.button("Leave mission", type="tertiary", key="btn_leave_end", on_click=leave, args=(go,))
        flash_box()
    with right:
        with st.container(key="card_results"):
            tab = ui.tabs(["Standings", "Mission trajectory"], key="results_tab", label="Results")
            if tab == "Standings":
                st.markdown(W.standings(final, ss.pid), unsafe_allow_html=True)
            else:
                trajectory_chart(state, final)


def trajectory_chart(state: dict, final: list[dict]) -> None:
    hist = state.get("history") or []
    palette = ["#FACC15", "#A78BFA", "#22D3EE", "#EC4899", "#34D399", "#F97316", "#60A5FA", "#F472B6"]
    fig = go_.Figure()
    xs = list(range(0, len(hist) + 1))
    for i, r in enumerate(final[:8]):
        ys = [0] + [h.get(r["id"], 0) for h in hist]
        is_me = r["id"] == st.session_state.pid
        fig.add_trace(go_.Scatter(
            x=xs, y=ys, mode="lines+markers", name=f"{r['avatar']} {r['name']}",
            line=dict(color=palette[i % len(palette)], width=4 if is_me else 2.4, shape="spline", smoothing=0.6),
            marker=dict(size=7 if is_me else 5),
        ))
    fig.update_layout(
        height=330, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Space Grotesk, sans-serif", color="#C7CCEB"),
        legend=dict(orientation="h", y=-0.2), hovermode="x unified",
        xaxis=dict(title="Question", gridcolor="rgba(160,172,255,.08)", dtick=1, zeroline=False),
        yaxis=dict(title="Score", gridcolor="rgba(160,172,255,.08)", zeroline=False),
    )
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False}, key="traj_chart")


# ---------------------------------------------------------------- entry
def render(go) -> None:
    ss = st.session_state

    @st.fragment(run_every=1.0)
    def live_screen():
        if ss.view != "live" or not ss.code:
            st.rerun()  # a callback (e.g. Leave) changed the view: redraw the whole app
        res = rpc.call("get_room_state", ss.code, ss.pid)
        if not res.get("ok"):
            st.markdown(W.alert(res.get("error", "Lost contact with the mission.")), unsafe_allow_html=True)
            if not res.get("offline"):
                if st.button("Back to launch pad", type="primary", key="btn_lost"):
                    ss.code = ss.pid = None
                    st.query_params.clear()
                    go("home")
                    st.rerun()
            else:
                st.markdown(W.loader("Trying to re-establish the uplink…"), unsafe_allow_html=True)
                st.button("Abort and leave", type="tertiary", key="btn_abort", on_click=leave, args=(go,))
            return

        state = res["state"]
        phase = state["phase"]
        if phase in ("lobby", "launch"):
            lobby(state, go)
            if phase == "launch":
                offset = stable(("launch", ss.code, state["games_played"]), state["duration"] - state["time_left"])
                st.markdown(W.launch_overlay(offset), unsafe_allow_html=True)
        elif phase in ("question", "reveal"):
            question_view(state)
        elif phase == "finished":
            finished_view(state, go)

    live_screen()
