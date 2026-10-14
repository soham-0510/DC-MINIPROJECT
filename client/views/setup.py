"""Mission planning: category, difficulty, number of questions, time per question."""

from __future__ import annotations

import streamlit as st
import streamlit_shadcn_ui as ui

import rpc
from components import widgets as W

DIFFS = ["mixed", "easy", "medium", "hard"]
DIFF_NAMES = {"mixed": "Mixed ramp", "easy": "Cadet · easy", "medium": "Pilot · medium", "hard": "Commander · hard"}


def category_grid(cats: list[dict], selected: str, key_prefix: str = "") -> None:
    ss = st.session_state
    rows = [cats[i:i + 4] for i in range(0, len(cats), 4)]
    for row in rows:
        cols = st.columns(4)
        for col, cat in zip(cols, row):
            with col:
                kind = "catsel_" if cat["id"] == selected else "cat_"
                with st.container(key=f"{kind}{key_prefix}{cat['id']}"):
                    label = f"**{cat['icon']}  {cat['title']}**\n{cat['count']} questions · {cat['blurb']}"
                    if st.button(label, key=f"pick_{key_prefix}{cat['id']}", width="stretch"):
                        ss.setup_category = cat["id"]
                        st.rerun()


def mission_controls(prefix: str = "") -> tuple[str, int, int]:
    ss = st.session_state
    c1, c2, c3 = st.columns([1.4, 1, 1], gap="large")
    with c1:
        st.markdown(W.section("Difficulty", "Mixed starts easy and ramps up."), unsafe_allow_html=True)
        diff = ui.tabs(DIFFS, value=ss.setup_difficulty, format_func=lambda d: DIFF_NAMES[d].split(" ·")[0],
                       key=f"{prefix}diff_tabs", label="Difficulty")
    with c2:
        st.markdown(W.section("Questions", "How long is the mission?"), unsafe_allow_html=True)
        n = ui.slider("Number of questions", 3, 20, value=ss.setup_num, step=1, key=f"{prefix}num_slider")
    with c3:
        st.markdown(W.section("Clock", "Seconds per question."), unsafe_allow_html=True)
        t = ui.slider("Seconds per question", 10, 30, value=ss.setup_time, step=5, key=f"{prefix}time_slider")
    n = int(n[0] if isinstance(n, (list, tuple)) else n)
    t = int(t[0] if isinstance(t, (list, tuple)) else t)
    ss.setup_difficulty, ss.setup_num, ss.setup_time = diff, n, t
    return diff, n, t


def render(go) -> None:
    ss = st.session_state
    ss.setdefault("setup_category", "random")
    ss.setdefault("setup_difficulty", "mixed")
    ss.setdefault("setup_num", 10)
    ss.setdefault("setup_time", 15)

    if st.button("← Back to launch pad", type="tertiary", key="setup_back"):
        go("home")
        st.rerun()

    st.markdown('<h2 style="margin:4px 0 2px;font-size:1.9rem">Plan your mission</h2>'
                '<div class="section-sub">Choose where in the universe your crew is heading.</div>',
                unsafe_allow_html=True)

    cats = st.session_state.get("_cats")
    if not cats:
        res = rpc.call("get_categories")
        if not res.get("ok"):
            st.markdown(W.alert(res.get("error", "Couldn't load categories.")), unsafe_allow_html=True)
            return
        cats = ss["_cats"] = res["categories"]

    category_grid(cats, ss.setup_category)
    st.write("")
    with st.container(key="card_controls"):
        diff, n, t = mission_controls()

    cat = next((c for c in cats if c["id"] == ss.setup_category), cats[0])
    st.write("")
    summary, action = st.columns([2, 1], vertical_alignment="center")
    with summary:
        st.markdown(W.settings_chips({"difficulty": diff, "num_questions": n, "time_per_q": t},
                                     cat["title"], cat["icon"]), unsafe_allow_html=True)
    with action:
        with st.container(key="launch_create"):
            if st.button("CREATE MISSION", type="primary", width="stretch", key="btn_create"):
                res = rpc.call("create_room", ss.name, ss.avatar, cat["id"], diff, n, t)
                if res.get("ok"):
                    ss.code, ss.pid = res["code"], res["player_id"]
                    st.query_params.update({"code": ss.code, "pid": ss.pid})
                    go("live")
                    st.rerun()
                else:
                    st.markdown(W.alert(res["error"]), unsafe_allow_html=True)
