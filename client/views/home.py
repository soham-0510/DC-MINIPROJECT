"""Launch Pad: hero, astronaut profile, host or join a mission."""

from __future__ import annotations

import streamlit as st
import streamlit_shadcn_ui as ui

import rpc
from components import widgets as W


def _categories() -> list[dict]:
    ss = st.session_state
    if not ss.get("_cats"):
        res = rpc.call("get_categories")
        if res.get("ok"):
            ss["_cats"] = res["categories"]
    return ss.get("_cats") or []


def _enter_live(res: dict, go) -> None:
    ss = st.session_state
    ss.code, ss.pid = res["code"], res["player_id"]
    if res.get("name"):
        ss.name = res["name"]
    st.query_params.update({"code": ss.code, "pid": ss.pid})
    go("live")


def render(go, avatars: list[str]) -> None:
    ss = st.session_state
    cats = _categories()
    total_q = cats[0]["count"] if cats else 119
    st.markdown(W.hero(total_q, max(len(cats) - 1, 6)), unsafe_allow_html=True)

    if ss.get("uplink_ok") is False:
        st.markdown(W.alert("The game server isn't answering. Start it with  python server/game_server.py  "
                            "or open Uplink above to set its address."), unsafe_allow_html=True)

    left, right = st.columns([1.15, 1], gap="large")

    with left:
        with st.container(key="card_profile"):
            st.markdown(W.section("Your astronaut", "This is how your crew will see you on the leaderboard."),
                        unsafe_allow_html=True)
            name = ui.input("Callsign", value=ss.name, key="callsign_input", placeholder="e.g. Nova Rider",
                            max_length=18)
            ss.name = (name or "").strip()
            with st.container(key="avatar_picker"):
                pick = st.pills("Choose your avatar", avatars, default=ss.avatar, key="avatar_pills",
                                selection_mode="single")
            if pick:
                ss.avatar = pick
            st.markdown(
                W.one_line(f"""<div class="crew-card me" style="margin-top:12px">
                <div class="av">{W.esc(ss.avatar)}</div><div>
                <div class="nm">{W.esc(ss.name or 'Unnamed astronaut')}</div>
                <span class="tag">Rank on arrival · 🛰️ Space Cadet</span></div></div>"""),
                unsafe_allow_html=True,
            )

    with right:
        with st.container(key="card_host"):
            st.markdown(W.section("Host a mission", "Pick a topic, set the clock, then share the code."),
                        unsafe_allow_html=True)
            with st.container(key="big_host"):
                if st.button("🚀  Plan a new mission", type="primary", width="stretch", key="btn_host"):
                    if not ss.name:
                        ss.flash = "Add a callsign first so your crew knows who's flying."
                    else:
                        go("setup")
                        st.rerun()

        with st.container(key="card_join"):
            st.markdown(W.section("Join a crew", "Enter the 6-character code shown on the host's screen."),
                        unsafe_allow_html=True)
            code = ui.input_otp("Mission code", pattern="alphanumeric", max_length=6, key="join_code")
            with st.container(key="big_join"):
                if st.button("🛸  Join mission", width="stretch", key="btn_join"):
                    code = (code or "").strip().upper()
                    if not ss.name:
                        ss.flash = "Add a callsign first so your crew knows who's flying."
                    elif len(code) != 6:
                        ss.flash = "Mission codes have 6 characters — check the host's screen."
                    else:
                        res = rpc.call("join_room", code, ss.name, ss.avatar)
                        if res.get("ok"):
                            _enter_live(res, go)
                            st.rerun()
                        ss.flash = res.get("error")

    if ss.flash:
        st.markdown(W.alert(ss.flash), unsafe_allow_html=True)
        ss.flash = None

    st.markdown(
        W.one_line("""<div class="section-sub" style="text-align:center;margin-top:28px">
        Every tap here becomes a remote method call — <span class="mono">create_room()</span>,
        <span class="mono">join_room()</span>, <span class="mono">submit_answer()</span> — on one shared Pyro5 game server.
        Open <b>Ground Station</b> to watch them arrive live.</div>"""),
        unsafe_allow_html=True,
    )
