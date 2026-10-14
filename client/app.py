"""
AstroQuiz Arena — Streamlit client (one per player).

    streamlit run client/app.py

Each browser tab is an independent RPC client of the shared game server.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

import rpc  # noqa: E402
import theme  # noqa: E402
from components import widgets as W  # noqa: E402
from views import ground_station, home, live, setup  # noqa: E402

st.set_page_config(
    page_title="AstroQuiz Arena",
    page_icon="🪐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

AVATARS = ["🧑‍🚀", "👽", "🚀", "🛸", "🌙", "☄️", "🪐", "🌟", "🛰️", "🤖"]


def init_state() -> None:
    ss = st.session_state
    rpc.init_connection_state()
    ss.setdefault("view", "home")
    ss.setdefault("name", "")
    ss.setdefault("avatar", AVATARS[0])
    ss.setdefault("code", None)
    ss.setdefault("pid", None)
    ss.setdefault("flash", None)
    ss.setdefault("anim", {})
    ss.setdefault("prev_view", "home")
    # Restore a running mission after a browser refresh (code & player id live in the URL)
    if not ss.get("_restored"):
        ss["_restored"] = True
        qp = st.query_params
        if qp.get("code") and qp.get("pid"):
            ss.code, ss.pid = qp["code"], qp["pid"]
            ss.view = "live"
        if qp.get("server"):
            host, _, port = qp["server"].partition(":")
            ss.server_host = host
            if port.isdigit():
                ss.server_port = int(port)


def go(view: str) -> None:
    st.session_state.prev_view = st.session_state.view
    st.session_state.view = view


def hud() -> None:
    ss = st.session_state
    tools_key = "hud_tools_live" if ss.view == "live" else "hud_tools"
    left, mid, right = st.columns([5, 3.4, 1.7], vertical_alignment="center")
    with left:
        st.markdown(W.brand(), unsafe_allow_html=True)
    with mid, st.container(key=f"{tools_key}_a"):
        ok = ss.get("uplink_ok", True)
        lat = ss.get("last_latency_ms")
        lat_txt = f" · {lat:.0f} ms" if (ok and lat is not None) else ""
        dot = "🟢" if ok else "🔴"
        with st.popover(f"{dot} Uplink  {rpc.uplink_label()}{lat_txt}", width="stretch"):
            st.markdown(W.section("Game server connection",
                                  "Point this client at the computer running game_server.py."),
                        unsafe_allow_html=True)
            use_ns = st.toggle("Find the server through the Pyro5 Name Server", value=ss.use_ns,
                               help="Looks up 'astroquiz.server' by name — like Naming.lookup() in Java RMI.")
            if use_ns:
                ns_host = st.text_input("Name Server host", value=ss.ns_host)
                host, port = ss.server_host, ss.server_port
            else:
                c1, c2 = st.columns([2, 1])
                host = c1.text_input("Server IP / host", value=ss.server_host)
                port = c2.number_input("Port", value=int(ss.server_port), min_value=1, max_value=65535, step=1)
                ns_host = ss.ns_host
            if st.button("Save & test uplink", type="primary", width="stretch"):
                ss.use_ns, ss.ns_host = use_ns, ns_host.strip() or "localhost"
                ss.server_host, ss.server_port = host.strip() or "localhost", int(port)
                rpc.reset()
                res = rpc.call("ping")
                if res.get("ok"):
                    st.success(f"Connected · {ss.last_latency_ms:.0f} ms round-trip")
                else:
                    st.error(res["error"])
    with right, st.container(key=f"{tools_key}_b"):
        if ss.view == "ground":
            if st.button("← Back", width="stretch", key="hud_back"):
                go(ss.prev_view if ss.prev_view != "ground" else "home")
                st.rerun()
        else:
            if st.button("📡 Ground Station", width="stretch", key="hud_gs",
                         help="Live server monitor: rooms, clients and every RPC call"):
                go("ground")
                st.rerun()


def main() -> None:
    init_state()
    theme.inject_theme()
    theme.cosmos()
    hud()
    view = st.session_state.view
    if view == "setup":
        setup.render(go)
    elif view == "live" and st.session_state.code:
        live.render(go)
    elif view == "ground":
        ground_station.render()
    else:
        home.render(go, AVATARS)


main()
